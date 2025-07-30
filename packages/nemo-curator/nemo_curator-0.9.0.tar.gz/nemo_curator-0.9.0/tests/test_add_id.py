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

import dask.dataframe as dd
import pandas as pd
import pytest
from pytest import FixtureRequest

import nemo_curator as nc
from nemo_curator.datasets import DocumentDataset
from nemo_curator.utils.import_utils import gpu_only_import, is_unavailable

cudf = gpu_only_import("cudf")
is_cudf_available = not is_unavailable(cudf)


def list_to_dataset(
    documents: list[str], col_name: str = "text", npartitions: int = 2, backend: str = "pandas"
) -> DocumentDataset:
    data = {col_name: documents}
    pdf = pd.DataFrame(data)
    ddf = dd.from_pandas(pdf, npartitions=npartitions)
    if backend == "cudf" and is_unavailable(cudf):
        msg = "cuDF is not installed or importable."
        raise ImportError(msg)
    ddf = ddf.to_backend(backend)
    return DocumentDataset(ddf)


@pytest.fixture(params=["pandas", pytest.param("cudf", marks=pytest.mark.gpu)])
def single_partition_dataset(request: FixtureRequest) -> DocumentDataset:
    return list_to_dataset(
        ["First", "Second", "Third", "Fourth", "Fifth"],
        npartitions=1,
        backend=request.param,
    )


@pytest.fixture(params=["pandas", pytest.param("cudf", marks=pytest.mark.gpu)])
def two_partition_dataset(request: FixtureRequest) -> DocumentDataset:
    return list_to_dataset(
        ["First", "Second", "Third", "Fourth", "Fifth"],
        npartitions=2,
        backend=request.param,
    )


class TestAddId:
    def test_basic_id(self, single_partition_dataset: DocumentDataset) -> None:
        id_field = "id"
        add_id = nc.AddId(id_field, start_index=0)
        id_dataset = add_id(single_partition_dataset)
        actual_ids = id_dataset.df[id_field].compute()
        expected_ids = pd.Series(
            [
                "doc_id-0000000000",
                "doc_id-0000000001",
                "doc_id-0000000002",
                "doc_id-0000000003",
                "doc_id-0000000004",
            ]
        )
        if is_cudf_available and isinstance(actual_ids, cudf.Series):
            actual_ids = actual_ids.to_pandas()

        assert all(expected_ids == actual_ids), f"Expected: {expected_ids}, got: {actual_ids}"

    def test_two_partitions(self, two_partition_dataset: DocumentDataset) -> None:
        id_field = "id"
        add_id = nc.AddId(id_field, start_index=0)
        id_dataset = add_id(two_partition_dataset)
        actual_ids = id_dataset.df[id_field].compute()
        expected_ids = pd.Series(
            [
                "doc_id-0000000000",
                "doc_id-0000000001",
                "doc_id-0000000002",
                "doc_id-0000000003",
                "doc_id-0000000004",
            ]
        )
        if is_cudf_available and isinstance(actual_ids, cudf.Series):
            actual_ids = actual_ids.to_pandas()

        assert all(expected_ids == actual_ids), f"Expected: {expected_ids}, got: {actual_ids}"

    def test_id_prefix(self, two_partition_dataset: DocumentDataset) -> None:
        id_field = "id"
        id_prefix = "my_id"
        add_id = nc.AddId(id_field, id_prefix=id_prefix, start_index=0)
        id_dataset = add_id(two_partition_dataset)
        actual_ids = id_dataset.df[id_field].compute()
        expected_ids = pd.Series(
            [
                f"{id_prefix}-0000000000",
                f"{id_prefix}-0000000001",
                f"{id_prefix}-0000000002",
                f"{id_prefix}-0000000003",
                f"{id_prefix}-0000000004",
            ]
        )
        if is_cudf_available and isinstance(actual_ids, cudf.Series):
            actual_ids = actual_ids.to_pandas()

        assert all(expected_ids == actual_ids), f"Expected: {expected_ids}, got: {actual_ids}"

    def test_start_index(self, two_partition_dataset: DocumentDataset) -> None:
        id_field = "id"
        start_index = 13
        add_id = nc.AddId(id_field, start_index=start_index)
        id_dataset = add_id(two_partition_dataset)
        actual_ids = id_dataset.df[id_field].compute()
        expected_ids = pd.Series(
            [
                "doc_id-0000000013",
                "doc_id-0000000014",
                "doc_id-0000000015",
                "doc_id-0000000016",
                "doc_id-0000000017",
            ]
        )
        if is_cudf_available and isinstance(actual_ids, cudf.Series):
            actual_ids = actual_ids.to_pandas()

        assert all(expected_ids == actual_ids), f"Expected: {expected_ids}, got: {actual_ids}"

    def test_fast_id_single_partition(self, single_partition_dataset: DocumentDataset) -> None:
        id_field = "id"
        add_id = nc.AddId(id_field)
        id_dataset = add_id(single_partition_dataset)
        actual_ids = id_dataset.df[id_field].compute()
        expected_ids = pd.Series(
            [
                "doc_id-00",
                "doc_id-10",
                "doc_id-20",
                "doc_id-30",
                "doc_id-40",
            ]
        )
        if is_cudf_available and isinstance(actual_ids, cudf.Series):
            actual_ids = actual_ids.to_pandas()

        assert all(expected_ids == actual_ids), f"Expected: {expected_ids}, got: {actual_ids}"

    def test_fast_id_two_partitions(self, two_partition_dataset: DocumentDataset) -> None:
        id_field = "id"
        add_id = nc.AddId(id_field)
        id_dataset = add_id(two_partition_dataset)
        actual_ids = id_dataset.df[id_field].compute()
        expected_ids = pd.Series(
            [
                "doc_id-00",
                "doc_id-10",
                "doc_id-20",
                "doc_id-01",
                "doc_id-11",
            ]
        )
        if is_cudf_available and isinstance(actual_ids, cudf.Series):
            actual_ids = actual_ids.to_pandas()

        assert all(expected_ids == actual_ids), f"Expected: {expected_ids}, got: {actual_ids}"
