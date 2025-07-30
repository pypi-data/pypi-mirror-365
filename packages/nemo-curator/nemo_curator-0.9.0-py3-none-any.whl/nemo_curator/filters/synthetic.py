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

import json

import numpy as np
import pandas as pd
from openai import OpenAI

from nemo_curator.filters.doc_filter import DocumentFilter
from nemo_curator.utils.decorators import batched
from nemo_curator.utils.distributed_utils import NoWorkerError, load_object_on_worker


def create_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
    )


# ----------------------------------------------------------------------------80
# ------------------------ EASINESS FILTER -------------------------------------
# ----------------------------------------------------------------------------80
class EasinessFilter(DocumentFilter):
    """
    Discards questions that are deemed easy to retrieve by retriever modls
    """

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_key: str,
        model: str,
        percentile: float = 0.7,
        truncate: str = "NONE",
        batch_size: int = 1,
        text_fields: list[str] | None = None,
    ):
        self._name = "easiness_filter"
        self.base_url = base_url
        self.api_key = api_key
        self.nim_model = model
        self.percentile = percentile
        if truncate:
            self.truncate = truncate
        self.batch_size = batch_size
        if text_fields is None:
            self.text_fields = ["text", "question"]
        else:
            self.text_fields = text_fields

    @batched
    def score_document(self, df: pd.DataFrame) -> pd.Series:
        try:
            self.client = load_object_on_worker(
                attr="openai_client_easiness",
                load_object_function=create_client,
                load_object_kwargs={"base_url": self.base_url, "api_key": self.api_key},
            )
        except NoWorkerError:
            return pd.Series(np.ones(len(df)), dtype=float)

        document_score = self._calc_similarity_nim(
            df[self.text_fields[0]].to_list(), df[self.text_fields[1]].to_list()
        )
        return pd.Series(document_score, index=df.index)

    @batched
    def keep_document(self, scores: pd.Series) -> pd.Series:
        filter_threshold = np.percentile(scores, self.percentile)
        return scores <= filter_threshold

    def _get_nim_embedding(self, text: str | list[str], input_type: str) -> float | np.ndarray | None:
        # Obtain embeddings from nim model
        if isinstance(text, list):
            input_ = text
        elif isinstance(text, str):
            input_ = [text]

        try:
            response = self.client.embeddings.create(
                input=input_,
                model=self.nim_model,
                encoding_format="float",
                extra_body={"input_type": input_type, "truncate": self.truncate},
            )
        except Exception as e:  # noqa: BLE001
            print(f"Error: {e}")
            response = None

        if response and not isinstance(response, str):
            if isinstance(text, list):
                embeddings = [r.embedding for r in response.data]
            elif isinstance(text, str):
                embeddings = response.data[0].embedding
            return embeddings
        else:
            return []

    def _calc_similarity_nim(self, context: str | list[str], question: str | list[str]) -> float | np.ndarray:
        # cosine similarity
        doc_embed = self._get_nim_embedding(text=context, input_type="passage")
        q_embed = self._get_nim_embedding(text=question, input_type="query")
        if isinstance(context, list) and isinstance(question, list):
            if doc_embed and q_embed:
                sim = np.diag(np.dot(np.array(doc_embed), np.array(q_embed).T))
            else:
                sim = np.zeros(len(context))
        elif doc_embed and q_embed:
            sim = np.dot(doc_embed, q_embed)
        else:
            sim = 0.0

        return sim


# ----------------------------------------------------------------------------80
# ----------------------- Answerability Filter ---------------------------------
# ----------------------------------------------------------------------------80


class AnswerabilityFilter(DocumentFilter):
    """
    Discards questions that are not answerable by content present in the
    context document
    """

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_key: str,
        model: str,
        answerability_system_prompt: str,
        answerability_user_prompt_template: str,
        num_criteria: int,
        text_fields: list[str] | None = None,
    ):
        self._name = "answerability_filter"
        self.base_url = base_url
        self.api_key = api_key
        self.model_name = model
        self.system_prompt = answerability_system_prompt
        self.user_prompt_template = answerability_user_prompt_template
        self.num_criteria = num_criteria
        if text_fields is None:
            self.text_fields = ["text", "question"]
        else:
            self.text_fields = text_fields

    @batched
    def score_document(self, df: pd.DataFrame) -> pd.Series:
        try:
            self.client = load_object_on_worker(
                attr="openai_client_answerability",
                load_object_function=create_client,
                load_object_kwargs={"base_url": self.base_url, "api_key": self.api_key},
            )
        except NoWorkerError:
            return pd.Series(["string"] * len(df))

        return df.progress_apply(
            lambda row: self._llm_as_judge(
                row[self.text_fields[0]],
                row[self.text_fields[1]],
            ),
            axis=1,
        )

    # ----------------------------------------------------------------------------80
    @batched
    def keep_document(self, scores: pd.Series) -> pd.Series:
        def _keep_document(score: str) -> bool:
            is_keep = True  # default is to keep
            try:
                json_ans = json.loads(score)
                for i in range(self.num_criteria):
                    if json_ans[f"criterion_{i + 1}"] != "Y":
                        # filter out data if any of the criteria fails
                        is_keep = False  # filter out
                        break
            except Exception as e:  # noqa: BLE001
                # If there is a parse error, keep the document
                print(f"Parse error {e}")

            return is_keep

        return scores.apply(_keep_document)

    def _llm_as_judge(self, context: str, question: str) -> str | None:
        user_query = self.system_prompt + "\n\n"
        user_query += self.user_prompt_template.format(context=context, question=question)

        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": user_query}],
                temperature=0.5,
                top_p=1,
                max_tokens=1024,
            )

            generation = completion.choices[0].message.content

        except Exception as e:  # noqa: BLE001
            print(f"API call error {e}")
            return None  # generation

        return generation


# ----------------------------------------------------------------------------80
