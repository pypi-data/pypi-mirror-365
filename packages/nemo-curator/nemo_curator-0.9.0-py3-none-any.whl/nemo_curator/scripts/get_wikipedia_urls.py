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

from nemo_curator.utils.download_utils import get_wikipedia_urls
from nemo_curator.utils.script_utils import ArgumentHelper


def main(args: argparse.Namespace) -> None:
    wikipedia_urls = get_wikipedia_urls(language=args.language, wikidumps_index_prefix=args.wikidumps_index_baseurl)
    with open(args.output_url_file, "w") as output_file:
        for url in wikipedia_urls:
            output_file.write(url)
            output_file.write("\n")


def attach_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    ArgumentHelper(parser).add_arg_language(help="Desired language of the Wikipedia dump.")
    parser.add_argument(
        "--output-url-file",
        type=str,
        default="wikipedia_urls_latest.txt",
        help="The output file to which the URLs containing the latest dump data will be written.",
    )
    parser.add_argument(
        "--wikidumps-index-baseurl",
        type=str,
        default="https://dumps.wikimedia.org",
        help="The base URL for all Wikipedia dumps.",
    )

    return parser


def console_script() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        """
Pulls URLs pointing to the latest Wikipedia dumps.
""",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    main(attach_args(parser).parse_args())
