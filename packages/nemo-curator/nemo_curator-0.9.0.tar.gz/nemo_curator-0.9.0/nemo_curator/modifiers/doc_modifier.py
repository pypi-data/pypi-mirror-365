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

from abc import ABC, abstractmethod
from typing import Literal


class DocumentModifier(ABC):
    def __init__(self):
        super().__init__()
        self._name = self.__class__.__name__
        self._sentences = None
        self._paragraphs = None
        self._ngrams = None

    @abstractmethod
    def modify_document(self, text: str) -> str:
        pass

    @property
    def backend(self) -> Literal["pandas", "cudf", "any"]:
        """
        The dataframe backend the modifier operates on.
        Can be 'pandas', 'cudf', or 'any'. Defaults to 'pandas'.
        Returns:
            str: A string representing the dataframe backend the modifier needs as input
        """
        return "pandas"
