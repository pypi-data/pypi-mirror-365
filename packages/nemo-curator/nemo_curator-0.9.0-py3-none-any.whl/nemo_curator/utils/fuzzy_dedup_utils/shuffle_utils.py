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


import cudf
import dask_cuda
import numpy as np
from dask import config
from packaging.version import Version

from nemo_curator._compat import query_planning_enabled
from nemo_curator.utils.fuzzy_dedup_utils.output_map_utils import build_partition

dask_cuda_version = Version(dask_cuda.__version__)
USE_EXCOMMS = (
    dask_cuda_version >= Version("23.10") and dask_cuda_version < Version("24.06")
) or dask_cuda_version >= Version("24.08")


def write_partitioned_file(df: cudf.DataFrame, output_path: str, partition_on: str, batch_id: int) -> cudf.Series:
    if len(df) == 0:
        return cudf.Series([True])

    cudf.io.parquet.write_to_dataset(
        df,
        output_path,
        partition_cols=[partition_on],
        filename=f"batch_{batch_id}.parquet",
    )
    return cudf.Series([True])


def rearange_by_column_direct(
    df: cudf.DataFrame,
    col: str,
    npartitions: int,
    ignore_index: bool,
    excomms_default: bool = USE_EXCOMMS,
) -> cudf.DataFrame:
    # Execute a "direct" shuffle operation without staging
    if config.get("explicit-comms", excomms_default):
        from dask_cuda.explicit_comms.dataframe.shuffle import (
            shuffle as explicit_comms_shuffle,
        )

        # Use explicit comms unless the user has
        # disabled it with the dask config system,
        # or we are using an older version of dask-cuda
        return explicit_comms_shuffle(
            df,
            [col],
            npartitions=npartitions,
            ignore_index=ignore_index,
        )

    elif query_planning_enabled():
        try:
            from dask.dataframe import dask_expr
        except ImportError:
            # TODO: Remove when pinned to dask>2024.12.1
            import dask_expr

        # Use the internal dask-expr API
        return dask_expr.new_collection(
            dask_expr._shuffle.RearrangeByColumn(  # noqa: SLF001
                frame=df.expr,
                partitioning_index=col,
                npartitions_out=npartitions,
                ignore_index=ignore_index,
                method="tasks",
                # Prevent staged shuffling by setting max_branch
                # to the number of input partitions + 1
                options={"max_branch": npartitions + 1},
            )
        )

    else:
        from dask.dataframe.shuffle import rearrange_by_column

        return rearrange_by_column(
            df,
            col=col,
            shuffle_method="tasks",
            # Prevent staged shuffling by setting max_branch
            # to the number of input partitions + 1
            max_branch=npartitions + 1,
            npartitions=npartitions,
            ignore_index=ignore_index,
        )


def get_shuffle_part_ids_df(
    agg_df: cudf.DataFrame,
    partition_on: str,
    output_col: str,
    size_col: str,
    num_workers: int = 0,
) -> cudf.DataFrame:
    sizes = agg_df[size_col].values
    max_text_bytes_per_part = int(np.iinfo(np.int32).max * 3)

    # Adjust max_text_bytes_per_part if the number of output
    # partitions is small compared to the number of workers.
    # Sometimes we just have very few output partitions to
    # deal with, and just need a larger batch
    npartitions_min = max(1, int(num_workers * 0.8))
    while True:
        output_ar = build_partition(sizes.get(), max_text_bytes_per_part)
        if output_ar.max() > npartitions_min or max_text_bytes_per_part < 2**24:
            break
        max_text_bytes_per_part = int(max_text_bytes_per_part // 2.0)

    df = cudf.DataFrame()
    df[partition_on] = agg_df[partition_on]
    df[output_col] = output_ar
    return df
