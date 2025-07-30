# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os

import dask.dataframe as dd

import nemo_curator
from nemo_curator import Sequential
from nemo_curator.datasets import DocumentDataset
from nemo_curator.utils.config_utils import build_filter_pipeline
from nemo_curator.utils.distributed_utils import get_client, read_data, write_to_disk
from nemo_curator.utils.file_utils import expand_outdir_and_mkdir, get_batched_files
from nemo_curator.utils.script_utils import ArgumentHelper


def get_dataframe_complement(original_df: dd.DataFrame, filtered_df: dd.DataFrame) -> dd.DataFrame:
    def partition_complement(part_original_df: dd.DataFrame, partition_info: dict | None = None) -> dd.DataFrame:
        if not partition_info:
            return part_original_df
        part_filtered_df = filtered_df.get_partition(partition_info["number"])
        complement_mask = ~part_original_df.index.isin(part_filtered_df.index.persist())
        return part_original_df[complement_mask]

    return original_df.map_partitions(partition_complement)


def get_score_fields(pipeline: Sequential) -> list[str]:
    score_fields = []
    for nc_module in pipeline.modules:
        if (isinstance(nc_module, (nemo_curator.Score, nemo_curator.ScoreFilter))) and nc_module.score_field:
            score_fields.append(nc_module.score_field)

    return score_fields


def write_scores(df: dd.DataFrame, output_dir: str) -> None:
    for column in df.columns:
        output_path = os.path.join(output_dir, f"{column}.txt")
        df[column].to_csv(
            output_path,
            single_file=True,
            encoding="utf-8",
            header=False,
            index=False,
            mode="a",
        )


def main(args: argparse.Namespace) -> None:  # noqa: C901, PLR0912
    client = get_client(**ArgumentHelper.parse_client_args(args))
    if args.device == "cpu":
        backend = "pandas"
    elif args.device == "gpu":
        backend = "cudf"
    else:
        msg = f'Invalid device "{args.device}". Please specify either "cpu" or "gpu".'
        raise ValueError(msg)

    # Make the output directories
    kept_document_dir = args.output_retained_document_dir
    removed_document_dir = args.output_removed_document_dir
    if kept_document_dir:
        expand_outdir_and_mkdir(kept_document_dir)
    if removed_document_dir:
        expand_outdir_and_mkdir(removed_document_dir)

    filter_pipeline = build_filter_pipeline(args.filter_config_file)
    score_fields = get_score_fields(filter_pipeline)

    for files in get_batched_files(
        args.input_data_dir,
        kept_document_dir,
        args.input_file_type,
        batch_size=args.batch_size,
    ):
        # Load the data and filter
        dataset = DocumentDataset(
            read_data(
                files,
                file_type=args.input_file_type,
                backend=backend,
                add_filename=True,
            )
        )
        curr_dataset = prev_dataset = dataset

        # Process each filter individually so we can track which documents are removed at each step
        for filter_module in filter_pipeline.modules:
            curr_dataset = filter_module(curr_dataset).persist()

            filter_field = None
            if isinstance(filter_module, nemo_curator.Filter):
                filter_field = filter_module.filter_field
            elif isinstance(filter_module, nemo_curator.ScoreFilter):
                filter_field = filter_module.score_field

            # Save the documents removed by the filter
            if removed_document_dir and filter_field:
                removed_df = get_dataframe_complement(prev_dataset.df, curr_dataset.df)
                removed_filter_dir = os.path.join(removed_document_dir, filter_field)
                expand_outdir_and_mkdir(removed_filter_dir)
                write_to_disk(
                    removed_df,
                    removed_filter_dir,
                    write_to_filename=True,
                    output_type=args.output_file_type,
                )
                prev_dataset = curr_dataset
        filtered_dataset = curr_dataset
        filtered_dataset = filter_pipeline(dataset).persist()

        # Write scores to separate directory
        if args.output_document_score_dir:
            if args.id_field is not None and args.id_field in filtered_dataset.df.columns:
                output_df = filtered_dataset.df[[args.id_field, *score_fields]]
            else:
                output_df = filtered_dataset.df[score_fields]
            write_scores(output_df, args.output_document_score_dir)

        # Remove scores if not logged
        if not args.log_scores:
            filtered_dataset = DocumentDataset(filtered_dataset.df.drop(columns=score_fields))

        # If kept_document_dir is specified, then create it
        if kept_document_dir is not None:
            write_to_disk(
                filtered_dataset.df,
                kept_document_dir,
                write_to_filename=True,
                output_type=args.output_file_type,
            )
        else:
            # Overwrite the existing files
            write_to_disk(
                filtered_dataset.df,
                args.input_data_dir,
                write_to_filename=True,
                output_type=args.output_file_type,
            )

    client.close()


def attach_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        """
    Main driver script for applying filters to documents distributed
    across dataset files. Inputs are an input directory consisting
    of dataset files and a configuration file defining the filter
    to be applied to the documents (see the config directory for some
    example configs). This script will then compute scores
    on each document within the corpus and then, if specified by
    the user, separate the documents based on the threshold
    specified for the filter.

    For an example of how to use this script
    (and apply to a corpus in distributed fashion), please see
    the examples directory of this repository.
  """,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    arg_helper = ArgumentHelper(parser)

    arg_helper.add_arg_batch_size()
    arg_helper.add_arg_input_data_dir()
    arg_helper.add_arg_input_file_type()
    arg_helper.add_arg_input_local_data_dir()
    arg_helper.add_arg_log_dir(default="./log/filter_docs")
    arg_helper.add_arg_output_file_type()
    arg_helper.add_distributed_args()
    parser.add_argument(
        "--filter-config-file",
        type=str,
        required=True,
        help="The input filter configuration file that contains the "
        "path to the filter module as well as the filter parameters.",
    )
    arg_helper.attach_bool_arg(
        parser,
        "filter-only",
        default=False,
        help="Specifying this flag will indicate to the code that only the "
        "filtering operation should be performed and that scores should not be "
        "computed. This flag should be specified if scores have been "
        "pre-computed on the documents (e.g., the code was run without the "
        "--output-retained-document-dir argument) and users desire to apply "
        "the filter using the pre-computed scores.",
    )
    parser.add_argument(
        "--id-field",
        type=str,
        default=None,
        help="The name of the field within each object of the dataset "
        "file that assigns a unqiue ID to each document. "
        "If this is specified and found within the object, a list of all "
        "IDs will be written to the output score directory such that each line"
        "is consistent with the lines of the written score files. ",
    )
    arg_helper.attach_bool_arg(
        parser,
        "keep-node-scores-tmp-dir",
        default=False,
        help="If multiple nodes are used when computing scores, "
        "each node will write out its scores to a temporary directory "
        "shared across all nodes. Then, the rank 0 node will "
        "concatenate all of the scores, creating the output file. "
        "By default, this directory is removed after concatenation, "
        "however users can keep this temporary directory by specifying "
        "the flag --keep-node-scores-tmp-dir.",
    )
    parser.add_argument(
        "--log-frequency",
        type=int,
        default=10000,
        help="The frequency with which to write log messages when "
        "computing scores. By default a log message will "
        "be written every 10000 documents in a file.",
    )
    arg_helper.attach_bool_arg(
        parser,
        "log-scores",
        default=False,
        help="Specifying this flag will cause the computed scores to be "
        "logged as additional keys for each document. This only applies to "
        'filters with "log_score: True" in the config. This can aid in '
        "performing an interactive quality check of the documents.",
    )
    parser.add_argument(
        "--output-document-score-dir",
        type=str,
        default=None,
        help="The output directory where the computed document scores will "
        "be written. For each filter, its score will be written to a separate "
        "file where each line of the file corresponds to the score computed "
        "for each document in the corpus within this directory. This only applies to "
        'filters with "log_score: True" in the config. If this directory is not '
        "specified, then filter scores will not be written.",
    )
    parser.add_argument(
        "--output-removed-document-dir",
        type=str,
        default=None,
        help="The output directory where documents that are removed during "
        "filtering will be written. This argument is mainly for quality control "
        "in order examine documents that are not preserved during filtering. "
        "If it is not specified and the output-retained-document-dir is specified, "
        "then only the retained documents will be written to disk.",
    )
    parser.add_argument(
        "--output-retained-document-dir",
        type=str,
        default=None,
        help="The output directory to where documents that are "
        "retained during filtering will be written. If this argument "
        "is not specified, then the document scores from the "
        "filter(s) will be written to the document metadata in place.",
    )

    return parser


def console_script() -> None:
    main(attach_args().parse_args())
