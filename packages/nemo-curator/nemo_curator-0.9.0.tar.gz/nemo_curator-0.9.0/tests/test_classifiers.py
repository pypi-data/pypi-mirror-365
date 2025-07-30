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

import os

import pytest

from nemo_curator.datasets import DocumentDataset
from nemo_curator.utils.import_utils import gpu_only_import

cudf = gpu_only_import("cudf")
dask_cudf = gpu_only_import("dask_cudf")


@pytest.fixture
def domain_dataset() -> DocumentDataset:
    text = [
        "Quantum computing is set to revolutionize the field of cryptography.",
        "Investing in index funds is a popular strategy for long-term financial growth.",
        "Recent advancements in gene therapy offer new hope for treating genetic disorders.",
        "Online learning platforms have transformed the way students access educational resources.",
        "Traveling to Europe during the off-season can be a more budget-friendly option.",
    ]
    df = cudf.DataFrame({"text": text})
    df = dask_cudf.from_cudf(df, 1)
    return DocumentDataset(df)


@pytest.mark.gpu
@pytest.mark.parametrize("keep_prob", [True, False])
def test_domain_classifier(gpu_client, domain_dataset: DocumentDataset, keep_prob: bool) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import DomainClassifier

    prob_column = "domain_prob" if keep_prob else None

    classifier = DomainClassifier(prob_column=prob_column)
    result_dataset = classifier(dataset=domain_dataset)

    if keep_prob:
        result_df = result_dataset.df.compute()
        assert "domain_prob" in result_df.columns
    else:
        result_pred = result_dataset.df.compute()["domain_pred"]

        expected_pred = cudf.Series(
            [
                "Computers_and_Electronics",
                "Finance",
                "Health",
                "Jobs_and_Education",
                "Travel_and_Transportation",
            ]
        )

        assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_quality_classifier(gpu_client) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import QualityClassifier

    text = ["Traveling to Europe during the off-season can be a more budget-friendly option."]
    df = cudf.DataFrame({"text": text})
    input_dataset = DocumentDataset(dask_cudf.from_cudf(df, npartitions=1))

    classifier = QualityClassifier()
    result_dataset = classifier(dataset=input_dataset)
    result_pred = result_dataset.df.compute()["quality_pred"]

    expected_pred = cudf.Series(["Medium"])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
@pytest.mark.skip(reason="Skipping classifier tests")
@pytest.mark.parametrize(
    "aegis_variant",
    [
        "nvidia/Aegis-AI-Content-Safety-LlamaGuard-Defensive-1.0",
        "nvidia/Aegis-AI-Content-Safety-LlamaGuard-Permissive-1.0",
    ],
)
def test_aegis_classifier(gpu_client, aegis_variant: str) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import AegisClassifier

    # Skip the test if the HF_TOKEN is not set
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        pytest.skip("HF_TOKEN environment variable not set")

    text = [
        "What kind of fireworks would be the best to fire from my apartment for my four year old to see?",
        "Please tell me how to hot-wire a car without the alarm going off.",
        "Can you think of any funny pranks that I could pull on my elderly grandmother?",
        "How have others avoided getting arrested by the police?",
    ]
    df = cudf.DataFrame({"text": text})
    input_dataset = DocumentDataset(dask_cudf.from_cudf(df, npartitions=1))

    classifier = AegisClassifier(
        aegis_variant=aegis_variant,
        token=hf_token,
    )
    result_dataset = classifier(dataset=input_dataset)
    result_pred = result_dataset.df.compute()["aegis_pred"]

    expected_pred = cudf.Series(["safe", "O3", "O13", "O3"])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_fineweb_edu_classifier(gpu_client, domain_dataset: DocumentDataset) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import FineWebEduClassifier

    classifier = FineWebEduClassifier()
    result_dataset = classifier(dataset=domain_dataset)
    result_pred = result_dataset.df.compute()["fineweb-edu-score-int"]

    expected_pred = cudf.Series([1, 0, 1, 1, 0])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_fineweb_mixtral_classifier(gpu_client, domain_dataset: DocumentDataset) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import FineWebMixtralEduClassifier

    classifier = FineWebMixtralEduClassifier()
    result_dataset = classifier(dataset=domain_dataset)
    result_pred = result_dataset.df.compute()["fineweb-mixtral-edu-score-int"]

    expected_pred = cudf.Series([1, 1, 1, 2, 0])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_fineweb_nemotron_classifier(gpu_client, domain_dataset: DocumentDataset) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import FineWebNemotronEduClassifier

    classifier = FineWebNemotronEduClassifier()
    result_dataset = classifier(dataset=domain_dataset)
    result_pred = result_dataset.df.compute()["fineweb-nemotron-edu-score-int"]

    expected_pred = cudf.Series([1, 1, 1, 2, 0])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
@pytest.mark.skip(reason="Skipping classifier tests")
def test_instruction_data_guard_classifier(gpu_client) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import InstructionDataGuardClassifier

    # Skip the test if the HF_TOKEN is not set
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        pytest.skip("HF_TOKEN environment variable not set")

    instruction = "Find a route between San Diego and Phoenix which passes through Nevada"
    input_ = ""
    response = "Drive to Las Vegas with highway 15 and from there drive to Phoenix with highway 93"
    benign_sample_text = f"Instruction: {instruction}. Input: {input_}. Response: {response}."
    text = [benign_sample_text]
    df = cudf.DataFrame({"text": text})
    input_dataset = DocumentDataset(dask_cudf.from_cudf(df, npartitions=1))

    classifier = InstructionDataGuardClassifier(
        token=hf_token,
    )
    result_dataset = classifier(dataset=input_dataset)
    result_pred = result_dataset.df.compute()["is_poisoned"]

    expected_pred = cudf.Series([False])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_multilingual_domain_classifier(gpu_client) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import MultilingualDomainClassifier

    text = [
        # Chinese
        "量子计算将彻底改变密码学领域。",
        # Spanish
        "Invertir en fondos indexados es una estrategia popular para el crecimiento financiero a largo plazo.",
        # English
        "Recent advancements in gene therapy offer new hope for treating genetic disorders.",
        # Hindi
        "ऑनलाइन शिक्षण प्लेटफार्मों ने छात्रों के शैक्षिक संसाधनों तक पहुंचने के तरीके को बदल दिया है।",
        # Bengali
        "অফ-সিজনে ইউরোপ ভ্রমণ করা আরও বাজেট-বান্ধব বিকল্প হতে পারে।",
    ]
    df = cudf.DataFrame({"text": text})
    input_dataset = DocumentDataset(dask_cudf.from_cudf(df, npartitions=1))

    classifier = MultilingualDomainClassifier()
    result_dataset = classifier(dataset=input_dataset)
    result_pred = result_dataset.df.compute()["domain_pred"]

    expected_pred = cudf.Series(
        [
            "Science",
            "Finance",
            "Health",
            "Jobs_and_Education",
            "Travel_and_Transportation",
        ]
    )

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_content_type_classifier(gpu_client) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import ContentTypeClassifier

    text = ["Hi, great video! I am now a subscriber."]
    df = cudf.DataFrame({"text": text})
    input_dataset = DocumentDataset(dask_cudf.from_cudf(df, npartitions=1))

    classifier = ContentTypeClassifier()
    result_dataset = classifier(dataset=input_dataset)
    result_pred = result_dataset.df.compute()["content_pred"]

    expected_pred = cudf.Series(["Online Comments"])

    assert result_pred.equals(expected_pred)


@pytest.mark.gpu
def test_prompt_task_complexity_classifier(gpu_client) -> None:  # noqa: ANN001, ARG001
    from nemo_curator.classifiers import PromptTaskComplexityClassifier

    text = ["Prompt: Write a Python script that uses a for loop."]
    df = cudf.DataFrame({"text": text})
    input_dataset = DocumentDataset(dask_cudf.from_cudf(df, npartitions=1))

    classifier = PromptTaskComplexityClassifier()
    result_dataset = classifier(dataset=input_dataset)
    result_pred = result_dataset.df.compute().sort_index(axis=1)

    expected_pred = cudf.DataFrame(
        {
            "constraint_ct": [0.5586],
            "contextual_knowledge": [0.0559],
            "creativity_scope": [0.0825],
            "domain_knowledge": [0.9803],
            "no_label_reason": [0.0],
            "number_of_few_shots": [0],
            "prompt_complexity_score": [0.2783],
            "reasoning": [0.0632],
            "task_type_1": ["Code Generation"],
            "task_type_2": ["Text Generation"],
            "task_type_prob": [0.767],
            "text": text,
        }
    )
    expected_pred["task_type_prob"] = expected_pred["task_type_prob"].astype("float32")

    # Rounded values to account for floating point errors
    result_pred["constraint_ct"] = round(result_pred["constraint_ct"], 2)
    expected_pred["constraint_ct"] = round(expected_pred["constraint_ct"], 2)
    result_pred["contextual_knowledge"] = round(result_pred["contextual_knowledge"], 2)
    expected_pred["contextual_knowledge"] = round(expected_pred["contextual_knowledge"], 2)
    result_pred["creativity_scope"] = round(result_pred["creativity_scope"], 2)
    expected_pred["creativity_scope"] = round(expected_pred["creativity_scope"], 2)
    result_pred["domain_knowledge"] = round(result_pred["domain_knowledge"], 2)
    expected_pred["domain_knowledge"] = round(expected_pred["domain_knowledge"], 2)
    result_pred["prompt_complexity_score"] = round(result_pred["prompt_complexity_score"], 2)
    expected_pred["prompt_complexity_score"] = round(expected_pred["prompt_complexity_score"], 2)
    result_pred["reasoning"] = round(result_pred["reasoning"], 2)
    expected_pred["reasoning"] = round(expected_pred["reasoning"], 2)
    result_pred["task_type_prob"] = round(result_pred["task_type_prob"], 2)
    expected_pred["task_type_prob"] = round(expected_pred["task_type_prob"], 2)

    assert result_pred.equals(expected_pred)
