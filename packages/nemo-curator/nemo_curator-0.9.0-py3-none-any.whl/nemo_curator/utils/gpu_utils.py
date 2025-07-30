# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
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

GPU_INSTALL_STRING = """Install GPU packages via `pip install --extra-index-url https://pypi.nvidia.com nemo-curator[cuda12x]`
or use `pip install --extra-index-url https://pypi.nvidia.com ".[cuda12x]"` if installing from source"""


def is_cudf_type(obj: object) -> bool:
    """
    Check if an object is a cuDF type
    """
    types = [
        str(type(obj)),
        str(getattr(obj, "_partition_type", "")),
        str(getattr(obj, "_meta", "")),
    ]
    return any("cudf" in obj_type for obj_type in types)
