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

import dask
import numpy as np
import pandas as pd
import pytest
from dask import dataframe as dd
from dask.dataframe.utils import assert_eq

from nemo_curator.datasets import DocumentDataset
from nemo_curator.datasets.parallel_dataset import ParallelDataset
from nemo_curator.filters import (
    AlphaFilter,
    BoilerPlateStringFilter,
    BulletsFilter,
    CommonEnglishWordsFilter,
    DocumentFilter,
    EllipsisFilter,
    GeneralCommentToCodeFilter,
    HistogramFilter,
    HTMLBoilerplateFilter,
    LengthRatioFilter,
    LongWordFilter,
    MeanWordLengthFilter,
    NonAlphaNumericFilter,
    NumberOfLinesOfCodeFilter,
    NumbersFilter,
    ParenthesesFilter,
    PerExtensionFilter,
    PornographicUrlsFilter,
    PunctuationFilter,
    PythonCommentToCodeFilter,
    RepeatedLinesByCharFilter,
    RepeatedLinesFilter,
    RepeatedParagraphsByCharFilter,
    RepeatedParagraphsFilter,
    RepeatingDuplicateNGramsFilter,
    RepeatingTopNGramsFilter,
    SubstringFilter,
    SymbolsToWordsFilter,
    TokenCountFilter,
    UrlsFilter,
    WhiteSpaceFilter,
    WordCountFilter,
    WordsWithoutAlphabetsFilter,
    XMLHeaderFilter,
)
from nemo_curator.filters.models.qe_models import COMET_IMPORT_MSG, PYMARIAN_IMPORT_MSG
from nemo_curator.modules import (
    Filter,
    ParallelScoreFilter,
    Score,
    ScoreFilter,
    Sequential,
)
from nemo_curator.utils.decorators import batched
from nemo_curator.utils.import_utils import is_unavailable, safe_import

comet = safe_import("comet", msg=COMET_IMPORT_MSG)
pymarian = safe_import("pymarian", msg=PYMARIAN_IMPORT_MSG)


class LetterCountFilter(DocumentFilter):
    """
    Keeps documents that have at least some number of a given letter
    """

    def __init__(self, letter: str = "a", min_count: int = 5) -> None:
        super().__init__()
        self.letter = letter
        self.min_count = min_count

    def score_document(self, text: str) -> int:
        return text.count(self.letter)

    def keep_document(self, score: int) -> bool:
        return score >= self.min_count


class BatchedLengthFilter(DocumentFilter):
    """
    Keeps documents of a given length
    """

    def __init__(self, min_length: int = 5, max_length: int = 10) -> None:
        super().__init__()
        self.min_length = min_length
        self.max_length = max_length

    @batched
    def score_document(self, df: pd.DataFrame) -> pd.Series:
        return df.str.len()

    @batched
    def keep_document(self, scores: pd.Series) -> pd.Series:
        min_threshold = self.min_length <= scores
        max_threshold = scores <= self.max_length
        return min_threshold & max_threshold


# A simple dummy tokenizer for our tests.
class DummyTokenizer:
    def encode(self, text: str) -> list[str]:
        # Simply splits the text on whitespace.
        return text.split()


def all_equal(left_dataset: DocumentDataset, right_dataset: DocumentDataset) -> bool:
    return all(left_dataset.df.compute() == right_dataset.df.compute())


def list_to_dataset(documents: list[str], col_name: str = "text", npartitions: int = 2) -> DocumentDataset:
    data = {col_name: documents}
    pdf = pd.DataFrame(data)

    return DocumentDataset(dd.from_pandas(pdf, npartitions=npartitions))


def two_lists_to_parallel_dataset(  # noqa: PLR0913
    src_documents: list[str],
    tgt_documents: list[str],
    src_lang: str,
    tgt_lang: str,
    src_col_name: str = "src",
    tgt_col_name: str = "tgt",
    npartitions: int = 2,
) -> ParallelDataset:
    src_langs = [src_lang] * len(src_documents)
    tgt_langs = [tgt_lang] * len(src_documents)
    data = {
        src_col_name: src_documents,
        "src_lang": src_langs,
        tgt_col_name: tgt_documents,
        "tgt_lang": tgt_langs,
    }
    pdf = pd.DataFrame(data)

    return ParallelDataset(dd.from_pandas(pdf, npartitions=npartitions))


@pytest.fixture
def letter_count_data() -> DocumentDataset:
    return list_to_dataset(["Two aa", "a a Three a", "Five aaa aa", "aaaSeven aaaa"], col_name="documents")


@pytest.fixture
def parallel_letter_count_data() -> ParallelDataset:
    return two_lists_to_parallel_dataset(
        ["Einsa", "Zwei aaa", "a Drei a", "Fünf aaa a", "aaaSieben aaaa"],
        ["aOne", "Two aa", "a a Three a", "Five aaa aa", "aaaSeven aaaa"],
        src_lang="de",
        tgt_lang="en",
        src_col_name="src",
        tgt_col_name="tgt",
    )


@pytest.fixture
def length_ratio_data() -> ParallelDataset:
    return two_lists_to_parallel_dataset(
        ["Test", "test", "Test Test ", "Test Test"],
        ["Prueba", "prueba prueba prueba", "Prueba Prueba", "Prueba Prueba Prueba "],
        src_lang="en",
        tgt_lang="es",
    )


class TestFilterModule:
    def test_score_filter(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        filter_step = ScoreFilter(letter_filter, text_field="documents")
        filtered_data = filter_step(letter_count_data)

        expected_indices = [2, 3]
        expected_data = DocumentDataset(letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_score(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "a_count"
        score_step = Score(
            letter_filter.score_document,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)

        expected_scores = pd.Series([2, 3, 5, 7])
        scores = scored_data.df[score_field]
        assert all(expected_scores == scores.compute()), f"Expected {expected_scores} but got {scores}"

    def test_score_document(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "a_count"
        score_step = Score(
            letter_filter,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)

        expected_scores = pd.Series([2, 3, 5, 7])
        scores = scored_data.df[score_field]
        assert all(expected_scores == scores.compute()), f"Expected {expected_scores} but got {scores}"

    def test_retain_score_filter(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "count_a"
        filter_step = ScoreFilter(letter_filter, text_field="documents", score_field=score_field)
        filtered_data = filter_step(letter_count_data)

        expected_indices = [2, 3]
        # Compute before loc due to https://github.com/dask/dask-expr/issues/1036
        expected_data = letter_count_data.df.compute().loc[expected_indices]
        expected_data = DocumentDataset(dd.from_pandas(expected_data, 2))
        expected_data.df[score_field] = pd.Series([5, 7], index=expected_data.df.index)
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_filter(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "a_count"
        score_step = Score(
            letter_filter.score_document,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)
        filter_step = Filter(letter_filter.keep_document, score_field)
        filtered_data = filter_step(scored_data)

        expected_indices = [2, 3]
        # Compute before loc due to https://github.com/dask/dask-expr/issues/1036
        expected_data = letter_count_data.df.compute().loc[expected_indices]
        expected_data = dd.from_pandas(expected_data, 2)
        expected_data[score_field] = pd.Series([5, 7], index=expected_data.index)
        expected_data = DocumentDataset(expected_data)
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_filter_document(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "a_count"
        score_step = Score(
            letter_filter,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)
        filter_step = Filter(letter_filter, score_field)
        filtered_data = filter_step(scored_data)

        expected_indices = [2, 3]
        # Compute before loc due to https://github.com/dask/dask-expr/issues/1036
        expected_data = letter_count_data.df.compute().loc[expected_indices]
        expected_data = dd.from_pandas(expected_data, 2)
        expected_data[score_field] = pd.Series([5, 7], index=expected_data.index)
        expected_data = DocumentDataset(expected_data)
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_invert(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        filter_step = ScoreFilter(letter_filter, text_field="documents", invert=True)
        filtered_data = filter_step(letter_count_data)

        expected_indices = [0, 1]
        expected_data = DocumentDataset(letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_sequential_filter(self, letter_count_data: DocumentDataset) -> None:
        filters = Sequential(
            [
                ScoreFilter(LetterCountFilter(), text_field="documents"),
                ScoreFilter(LetterCountFilter(min_count=6), text_field="documents"),
            ]
        )
        filtered_data = filters(letter_count_data)

        expected_indices = [3]
        expected_data = DocumentDataset(letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_batch_score_filter(self, letter_count_data: DocumentDataset) -> None:
        length_filter = BatchedLengthFilter(min_length=8, max_length=11)
        filter_step = ScoreFilter(length_filter, text_field="documents")
        filtered_data = filter_step(letter_count_data)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_batch_score(self, letter_count_data: DocumentDataset) -> None:
        length_filter = BatchedLengthFilter(min_length=8, max_length=11)
        score_field = "lengths"
        score_step = Score(
            length_filter.score_document,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)

        expected_scores = pd.Series([6, 11, 11, 13])
        scores = scored_data.df[score_field]
        assert all(expected_scores == scores.compute()), f"Expected {expected_scores} but got {scores}"

    def test_batch_score_document(self, letter_count_data: DocumentDataset) -> None:
        length_filter = BatchedLengthFilter(min_length=8, max_length=11)
        score_field = "lengths"
        score_step = Score(
            length_filter,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)

        expected_scores = pd.Series([6, 11, 11, 13])
        scores = scored_data.df[score_field]
        assert all(expected_scores == scores.compute()), f"Expected {expected_scores} but got {scores}"

    def test_batch_filter(self, letter_count_data: DocumentDataset) -> None:
        length_filter = BatchedLengthFilter(min_length=8, max_length=11)
        score_field = "lengths"
        score_step = Score(
            length_filter.score_document,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)
        filter_step = Filter(length_filter.keep_document, score_field)
        filtered_data = filter_step(scored_data)

        expected_indices = [1, 2]
        expected_data = letter_count_data.df.loc[expected_indices]
        expected_data[score_field] = pd.Series([11, 11], index=expected_data.index)
        expected_data = DocumentDataset(expected_data)
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_batch_filter_document(self, letter_count_data: DocumentDataset) -> None:
        length_filter = BatchedLengthFilter(min_length=8, max_length=11)
        score_field = "lengths"
        score_step = Score(
            length_filter,
            text_field="documents",
            score_field=score_field,
        )
        scored_data = score_step(letter_count_data)
        filter_step = Filter(length_filter, score_field)
        filtered_data = filter_step(scored_data)

        expected_indices = [1, 2]
        expected_data = letter_count_data.df.loc[expected_indices]
        expected_data[score_field] = pd.Series([11, 11], index=expected_data.index)
        expected_data = DocumentDataset(expected_data)
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_score_filter_type(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        filter_step = ScoreFilter(letter_filter, text_field="documents", score_type=int)
        filtered_data = filter_step(letter_count_data)

        expected_indices = [2, 3]
        expected_data = DocumentDataset(letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_score_type(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "a_count"
        score_step = Score(
            letter_filter.score_document,
            text_field="documents",
            score_field=score_field,
            score_type=int,
        )
        scored_data = score_step(letter_count_data)

        expected_scores = pd.Series([2, 3, 5, 7])
        scores = scored_data.df[score_field]
        assert all(expected_scores == scores.compute()), f"Expected {expected_scores} but got {scores}"

    def test_score_type_document(self, letter_count_data: DocumentDataset) -> None:
        letter_filter = LetterCountFilter()
        score_field = "a_count"
        score_step = Score(
            letter_filter,
            text_field="documents",
            score_field=score_field,
            score_type=int,
        )
        scored_data = score_step(letter_count_data)

        expected_scores = pd.Series([2, 3, 5, 7])
        scores = scored_data.df[score_field]
        assert all(expected_scores == scores.compute()), f"Expected {expected_scores} but got {scores}"

    def test_chain_filter(self, letter_count_data: DocumentDataset) -> None:
        letter_count_filter = LetterCountFilter(min_count=4)
        length_filter = BatchedLengthFilter(min_length=8, max_length=11)
        filters = Sequential(
            [
                ScoreFilter(letter_count_filter, text_field="documents"),
                ScoreFilter(length_filter, text_field="documents"),
            ]
        )
        filtered_data = filters(letter_count_data)

        expected_indices = [2]
        expected_data = DocumentDataset(letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_parallel_score_filter(self, parallel_letter_count_data: ParallelDataset) -> None:
        src_letter_count_filter = LetterCountFilter(min_count=2)
        tgt_letter_count_filter = LetterCountFilter(min_count=3)
        filter_step = ParallelScoreFilter(src_letter_count_filter, tgt_letter_count_filter)
        filtered_data = filter_step(parallel_letter_count_data)

        expected_indices = [2, 3, 4]
        expected_data = ParallelDataset(parallel_letter_count_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_joint_score_filter(self, length_ratio_data: ParallelDataset) -> None:
        filter_ = LengthRatioFilter(
            max_ratio=1.5,
            src_lang="en",
            tgt_lang="de",
            score_field="ratio",
            score_type=float,
        )
        filtered_data = filter_(length_ratio_data)

        expected_indices = [0, 2]
        expected_data = ParallelDataset(length_ratio_data.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"


class TestHeuristicFilters:
    def test_nonalpha(self) -> None:
        dataset = list_to_dataset(["", "This is a test case.", "%$^%$^%$&^$()))))", "$aaa"])
        filters = ScoreFilter(NonAlphaNumericFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_symbolswords(self) -> None:
        dataset = list_to_dataset(
            [
                "mixed bag ... #",
                "full of words",
                "... # ... # #",
                "barely ok 3 4 5 6 7 8 9 #",
            ]
        )
        filters = ScoreFilter(SymbolsToWordsFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_numbers(self) -> None:
        dataset = list_to_dataset(["purely letters", "34134543", "$!@$@!$!@", "abcdefghi1"])
        filters = ScoreFilter(NumbersFilter(max_number_to_text_ratio=0.1))
        filtered_data = filters(dataset)

        expected_indices = [0, 2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_urls(self) -> None:
        dataset = list_to_dataset(
            [
                "https://www.nvidia.com/en-us/",
                "no urls here!",
                "$!@$@!$!@",
                "bunch of other words with url afdsjafidsaofjbwreowihfdsafbdashuoiotauhiofdafdsafd fdasfdafdsafdsafdsafdsafdsafdsa https://www.nvidia.com/en-us/ something else after the url etc more and more",
                "words with url https://www.nvidia.com/en-us/",
            ]
        )
        filters = ScoreFilter(UrlsFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_bullets(self) -> None:
        dataset = list_to_dataset(
            [
                "• not good",
                "good",
                "50 \n ⦾ 50",
                "⁌ this \n⁌ should \n⁌barely \n⁌pass \n⁌5 \n⁌6 \n⁌7 \n⁌8 \n⁌9 \n done!",
            ]
        )
        filters = ScoreFilter(BulletsFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_whitespace(self) -> None:
        dataset = list_to_dataset(["\t\n\r", "good", "50%\n\n\n", "123\b"])
        filters = ScoreFilter(WhiteSpaceFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_parentheses(self) -> None:
        dataset = list_to_dataset(["()", "(not good)", "this is completely absolutely fine", "123456789("])
        filters = ScoreFilter(ParenthesesFilter())
        filtered_data = filters(dataset)

        expected_indices = [2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_longword(self) -> None:
        dataset = list_to_dataset(["tiny", "large"])
        filters = ScoreFilter(LongWordFilter(max_word_length=4))
        filtered_data = filters(dataset)

        expected_indices = [0]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_wordcount(self) -> None:
        dataset = list_to_dataset(["", "one", "two words", "$#@$ %$@$#@ !#@!", "one two three four five"])
        filters = ScoreFilter(WordCountFilter(min_words=2, max_words=4))
        filtered_data = filters(dataset)

        expected_indices = [2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_wordcount_zh(self) -> None:
        dataset = list_to_dataset(["", "你好。", "我喜欢学习中文。"])
        filters = ScoreFilter(WordCountFilter(min_words=2, max_words=5, lang="zh"))
        filtered_data = filters(dataset)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_wordcount_ja(self) -> None:
        dataset = list_to_dataset(["", "猫が寝ます。", "私は日本語のテキストを分割します。"])
        filters = ScoreFilter(WordCountFilter(min_words=5, max_words=11, lang="ja"))
        filtered_data = filters(dataset)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_boilerplate(self) -> None:
        dataset = list_to_dataset(
            [
                "nothing\t here",
                "1\n\n2\n\n3\n\n4\n\n5\n\n6\n\nterms of use\n\n privacy policy\n\n cookie policy\n\nuses cookies",
                "too much \n\n privacy & cookies policy",
            ]
        )
        filters = ScoreFilter(BoilerPlateStringFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 1]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_meanwordlength(self) -> None:
        dataset = list_to_dataset(
            [
                "a",
                "aa",
                "superlongword short",
                "evenly balanced",
                "waytoolongforasingleword",
            ]
        )
        filters = ScoreFilter(MeanWordLengthFilter())
        filtered_data = filters(dataset)

        expected_indices = [2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_repeatedlines(self) -> None:
        dataset = list_to_dataset(["totally unique", "half.\nhalf."])
        filters = ScoreFilter(RepeatedLinesFilter())
        filtered_data = filters(dataset)

        expected_indices = [0]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_repeatedparagraphs(self) -> None:
        dataset = list_to_dataset(["totally unique", "half.\n\nhalf."])
        filters = ScoreFilter(RepeatedParagraphsFilter())
        filtered_data = filters(dataset)

        expected_indices = [0]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_repeatedlineschar(self) -> None:
        dataset = list_to_dataset(
            [
                "totally unique",
                "a.\na.\nvery very very short duplicate.",
                "half.\nhalf.",
                "super very incredibly huge long duplicate.\nsuper very incredibly huge long duplicate.\na.\nb.\nc.",
            ]
        )
        filters = ScoreFilter(RepeatedLinesByCharFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 1]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_repeatedparagraphschar(self) -> None:
        dataset = list_to_dataset(
            [
                "totally unique",
                "a.\n\n  a.\n\n  very very very short duplicate.",
                "half.\n\nhalf.",
                "super very incredibly huge long duplicate.\n\nsuper very incredibly huge long duplicate.\n\n  a.\n\n  b.\n\n  c.",
            ]
        )
        filters = ScoreFilter(RepeatedParagraphsByCharFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 1]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_repeatingtopngrams(self) -> None:
        dataset = list_to_dataset(
            [
                "this is a totally fine sentence with no repeat ngrams so we are ok",
                "a b . a b",
                "a a a a a a",
                "totally fine small dupe a b a b",
            ]
        )
        filters = ScoreFilter(RepeatingTopNGramsFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_repeatingduplicatengrams(self) -> None:
        dataset = list_to_dataset(["a a b b a a b b", "totally fine", "a a a a this should be fine as well"])
        filters = ScoreFilter(RepeatingDuplicateNGramsFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_punctuation(self) -> None:
        dataset = list_to_dataset(["not good", "good.", "just\n barely\n fine\n ok\n yep."])
        filters = ScoreFilter(PunctuationFilter(max_num_sentences_without_endmark_ratio=0.8))
        filtered_data = filters(dataset)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_ellipsis(self) -> None:
        dataset = list_to_dataset(["not good...", "good.", "just...\n barely...\n fine...\n ok...\n yep."])
        filters = ScoreFilter(EllipsisFilter(max_num_lines_ending_with_ellipsis_ratio=0.8))
        filtered_data = filters(dataset)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_commonenglishwords(self) -> None:
        dataset = list_to_dataset(["uncommon", "the and", "the and and of to"])
        filters = ScoreFilter(CommonEnglishWordsFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_wordswithoutalphabets(self) -> None:
        dataset = list_to_dataset(["totally fine", "good good good good !", "@"])
        filters = ScoreFilter(WordsWithoutAlphabetsFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 1]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_pornographicurls(self) -> None:
        dataset = list_to_dataset(
            [
                "no url",
                "fine url https://www.nvidia.com/en-us/",
                "bad url https://www.pornhub.com/",
            ]
        )
        filters = ScoreFilter(PornographicUrlsFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 1]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_histogram(self) -> None:
        dataset = list_to_dataset(
            [
                "This is a perfectly fine English document.",
                "But if you insist that this is written in Chinese,",
                "it's likely that something is fishy.",
                "另一方面，这是一个好的中文文档，",  # noqa: RUF001
                "但你一定要说这是英文文档，",  # noqa: RUF001
                "那很可能有些地方出了差错。",
            ]
        )
        filter1 = ScoreFilter(HistogramFilter(lang="en"))
        filter2 = ScoreFilter(HistogramFilter(lang="zh"))

        expected_indices1 = [0, 1, 2]
        expected_indices2 = [3, 4, 5]
        expected_data1 = DocumentDataset(dataset.df.loc[expected_indices1])
        expected_data2 = DocumentDataset(dataset.df.loc[expected_indices2])

        filtered_data1 = filter1(dataset)
        filtered_data2 = filter2(dataset)
        assert all_equal(expected_data1, filtered_data1), f"Expected {expected_data1} but got {filtered_data1}"
        assert all_equal(expected_data2, filtered_data2), f"Expected {expected_data2} but got {filtered_data2}"


class TestTokenCountFilter:
    def test_score_document(self) -> None:
        tokenizer = DummyTokenizer()
        token_filter = TokenCountFilter(tokenizer, min_tokens=2, max_tokens=3)
        text = "another test case"  # Should yield 3 tokens.
        score = token_filter.score_document(text)
        assert score == 3  # noqa: PLR2004

    def test_keep_document(self) -> None:
        tokenizer = DummyTokenizer()
        token_filter = TokenCountFilter(tokenizer, min_tokens=2, max_tokens=3)
        # Check that a score of 1 (too few) and 4 (too many) are rejected,
        # while scores of 2 and 3 are accepted.
        assert token_filter.keep_document(2)
        assert token_filter.keep_document(3)
        assert not token_filter.keep_document(1)
        assert not token_filter.keep_document(4)

    def test_filter_dataset(self) -> None:
        # Create a dataset of documents with different word counts.
        docs = [
            "hello",  # 1 token
            "hello world",  # 2 tokens
            "this is a test",  # 4 tokens
            "another test case",  # 3 tokens
        ]
        dataset = list_to_dataset(docs, col_name="text")

        tokenizer = DummyTokenizer()
        token_filter = TokenCountFilter(tokenizer, min_tokens=2, max_tokens=3)
        filter_step = ScoreFilter(token_filter, text_field="text")
        filtered_dataset = filter_step(dataset)
        # Reset indices for filtered dataset to ensure identical labeling for comparison.
        filtered_dataset.df = filtered_dataset.df.reset_index(drop=True)

        # We expect to keep only the documents with exactly 2 or 3 tokens.
        expected_docs = [
            "hello world",  # 2 tokens
            "another test case",  # 3 tokens
        ]
        expected_dataset = list_to_dataset(expected_docs, col_name="text")
        # Reset indices for expected dataset to ensure identical labeling.
        expected_dataset.df = expected_dataset.df.reset_index(drop=True)
        assert all_equal(expected_dataset, filtered_dataset)

    def test_filter_dataset_default(self) -> None:
        # Create a dataset of documents with different word counts.
        docs = [
            "hello",  # 1 token
            "hello world",  # 2 tokens
            "this is a test",  # 4 tokens
            "another test case",  # 3 tokens
        ]
        dataset = list_to_dataset(docs, col_name="text")

        tokenizer = DummyTokenizer()
        # Using default settings: min_tokens=0 and max_tokens=inf, so all documents pass.
        token_filter = TokenCountFilter(tokenizer)
        filter_step = ScoreFilter(token_filter, text_field="text")
        filtered_dataset = filter_step(dataset)

        # We expect to keep all documents.
        expected_dataset = list_to_dataset(docs, col_name="text")
        assert all_equal(expected_dataset, filtered_dataset)


class TestSubstringFilter:
    def test_invalid_position(self) -> None:
        # Creating a SubstringFilter with an invalid position should raise a ValueError.
        with pytest.raises(ValueError):  # noqa: PT011
            SubstringFilter("foo", "middle")

    def test_prefix_mode(self) -> None:
        filter_prefix = SubstringFilter("Hello", "prefix")
        # Positive example: text starts with "Hello".
        text = "Hello world"
        score = filter_prefix.score_document(text)
        assert score == 1
        assert filter_prefix.keep_document(score)
        # Negative example: text does not start with "Hello".
        text2 = "world Hello"
        score2 = filter_prefix.score_document(text2)
        assert score2 == 0
        assert not filter_prefix.keep_document(score2)

    def test_suffix_mode(self) -> None:
        filter_suffix = SubstringFilter("end", "suffix")
        # Positive example: text ends with "end".
        text = "This is the end"
        score = filter_suffix.score_document(text)
        assert score == 1
        assert filter_suffix.keep_document(score)
        # Negative example: text does not end with "end".
        text2 = "The end is near"
        score2 = filter_suffix.score_document(text2)
        assert score2 == 0
        assert not filter_suffix.keep_document(score2)

    def test_any_mode(self) -> None:
        filter_any = SubstringFilter("test", "any")
        # Positive example: text contains "test".
        text = "this is a test string"
        score = filter_any.score_document(text)
        assert score == 1
        assert filter_any.keep_document(score)
        # Negative example: text does not contain "test".
        text2 = "this is a string"
        score2 = filter_any.score_document(text2)
        assert score2 == 0
        assert not filter_any.keep_document(score2)

    def test_filter_dataset_prefix(self) -> None:
        docs = ["Hello world", "world Hello", "Hello everyone", "Not matching"]
        dataset = list_to_dataset(docs, col_name="text")
        filter_prefix = SubstringFilter("Hello", "prefix")
        filter_step = ScoreFilter(filter_prefix, text_field="text")
        filtered_dataset = filter_step(dataset)

        # Expect only those records where the text starts with "Hello".
        expected_docs = ["Hello world", "Hello everyone"]
        expected_dataset = list_to_dataset(expected_docs, col_name="text")

        # Reset indices to ensure both DataFrames are identically labeled
        filtered_dataset = DocumentDataset(filtered_dataset.df.reset_index(drop=True))
        expected_dataset = DocumentDataset(expected_dataset.df.reset_index(drop=True))
        assert all_equal(expected_dataset, filtered_dataset)

    def test_filter_dataset_suffix(self) -> None:
        docs = [
            "This is the end",  # ends with "end"
            "end of story",  # does not end with "end"
            "ending is good",  # does not end with "end"
            "Not matching end",  # ends with "end"
            "The end",  # ends with "end"
        ]
        dataset = list_to_dataset(docs, col_name="text")
        filter_suffix = SubstringFilter("end", "suffix")
        filter_step = ScoreFilter(filter_suffix, text_field="text")
        filtered_dataset = filter_step(dataset)

        # Expect only those records that end with "end".
        expected_docs = [
            "Not matching end",
            "The end",
            "This is the end",
        ]
        expected_dataset = list_to_dataset(expected_docs, col_name="text")

        # Compare only the 'text' column values to avoid index label issues.
        filtered_dataset = DocumentDataset(filtered_dataset.df.reset_index(drop=True))
        expected_dataset = DocumentDataset(expected_dataset.df.reset_index(drop=True))
        assert_eq(expected_dataset.df["text"], filtered_dataset.df["text"])

    def test_filter_dataset_any(self) -> None:
        docs = ["test case", "This is a testcase", "no match here", "another test"]
        dataset = list_to_dataset(docs, col_name="text")
        filter_any = SubstringFilter("test", "any")
        filter_step = ScoreFilter(filter_any, text_field="text")
        filtered_dataset = filter_step(dataset)

        # Expect documents that contain "test" anywhere.
        expected_docs = ["test case", "This is a testcase", "another test"]
        expected_dataset = list_to_dataset(expected_docs, col_name="text")

        # Reset indices to ensure both DataFrames are identically labeled
        filtered_dataset = DocumentDataset(filtered_dataset.df.reset_index(drop=True))
        expected_dataset = DocumentDataset(expected_dataset.df.reset_index(drop=True))
        assert all_equal(expected_dataset, filtered_dataset)


class TestCodeFilters:
    def test_python_comment_to_code(self) -> None:
        doc_1 = "# Good code\nprint('hello world')"
        doc_2 = "print('bad code')"
        doc_3 = "# Too many\n# comments!"
        doc_4 = "'''Good comment'''\nprint('hello world')"
        dataset = list_to_dataset([doc_1, doc_2, doc_3, doc_4])
        filters = ScoreFilter(PythonCommentToCodeFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_general_commment_to_code(self) -> None:
        doc_1 = '// Good code\nprintf("hello world\\n")'
        doc_2 = 'printf("bad code\\n")'
        doc_3 = "// Way far too many\n// comments!"
        doc_4 = '/*\nGood comment\n*/\nprintf("hello world\\n")'
        dataset = list_to_dataset([doc_1, doc_2, doc_3, doc_4])
        filters = ScoreFilter(GeneralCommentToCodeFilter("text/x-c++"))
        filtered_data = filters(dataset)

        expected_indices = [0, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_number_lines_code(self) -> None:
        doc_1 = """print("too short")"""
        doc_2 = """print("just")
        print("right")"""
        doc_3 = """print("way")
        print("too")
        print("long")
        print("!")"""
        dataset = list_to_dataset([doc_1, doc_2, doc_3])
        filters = ScoreFilter(NumberOfLinesOfCodeFilter(min_lines=2, max_lines=3))
        filtered_data = filters(dataset)

        expected_indices = [1]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_xml_header(self) -> None:
        dataset = list_to_dataset(["no header", "<?xml version=1.0>", "slightly offset <?xml version="])
        filters = ScoreFilter(XMLHeaderFilter())
        filtered_data = filters(dataset)

        expected_indices = [0]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_alpha(self) -> None:
        dataset = list_to_dataset(["full of alphabet", "<>?$#@!", "mixed <>"])
        filters = ScoreFilter(AlphaFilter())
        filtered_data = filters(dataset)

        expected_indices = [0, 2]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_html_boilerplate(self) -> None:
        good_doc = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sample Webpage</title>
        </head>
        <body>
            <h1>Welcome to my sample webpage</h1>
            <p>This is a very fun paragraph on my sample webpage.</p>
        </body>
        </html>
        """
        boilerplate_heavy_doc = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Boilerplate Webpage</title>
        </head>
        <body>
            <h1><span>Welcome</span> <span>to</span> <span>my</span> <span>boilerplate</span> <span>webpage</span></h1>
            <div>
                <div>
                    <div><p>hi</p></div>
                </div>
                <div>
                    <div><p>hi</p></div>
                </div>
            </div>
        </body>
        </html>
        """
        small_doc = """
            <!DOCTYPE html>
            <html><body>hello world</body></html>
        """
        dataset = list_to_dataset([good_doc, boilerplate_heavy_doc, small_doc])
        filters = ScoreFilter(HTMLBoilerplateFilter())
        filtered_data = filters(dataset)

        expected_indices = [0]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    @pytest.fixture
    def per_extension_filter(self) -> PerExtensionFilter:
        metadata_file = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "nemo_curator",
                "utils",
                "code_meta.csv",
            )
        )

        return PerExtensionFilter("c++", "cpp", metadata_file=metadata_file)

    def test_per_extension_filter(self, per_extension_filter: PerExtensionFilter) -> None:
        good_cpp = """
        #include <iostream>
        using namespace std;
        int main() {
            cout << "Hello World!" << endl;
            return 0;
        };
        """
        dataset = list_to_dataset([good_cpp])
        filters = ScoreFilter(per_extension_filter)
        filtered_data = filters(dataset)
        expected_indices = [0]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])

        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    @pytest.mark.parametrize(
        # TODO: Check if this is correct.
        "content,expected",  # noqa: PT006
        [
            ("", (0, 0.0)),
            ("\n", (0, 0.0)),
            ("abc\n", (3, 1.5)),
            ("Lorem ipsum \ndolor sit amet,", (15, 13.5)),
        ],
    )
    def test_line_statistics(
        self, per_extension_filter: PerExtensionFilter, content: str, expected: tuple[int, float]
    ) -> None:
        line_statistics = per_extension_filter._line_statistics(content)  # noqa: SLF001
        assert line_statistics == expected, f"Expected {expected} but got {line_statistics}"


class FakeQualityFilter(DocumentFilter):
    """
    Emulates FastTextQualityFilter without a model
    """

    def __init__(self, alpha: float = 3, seed: int = 42):
        super().__init__()
        self._alpha = alpha
        self._seed = np.random.seed(seed)  # noqa: NPY002

    @batched
    def score_document(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(np.arange(len(df)) / len(df))

    @batched
    def keep_document(self, df: pd.DataFrame) -> pd.Series:
        return np.random.pareto(self._alpha, size=len(df)) > 1 - df  # noqa: NPY002


class FakeLangId(DocumentFilter):
    """
    Emulates FastTextLangId without a model
    """

    def __init__(self, min_langid_score: float = 0.3, convert_string: bool = False):
        super().__init__()
        self._cutoff = min_langid_score

        # Dask will automatically convert the list score type
        # to a string without this option.
        # See https://github.com/NVIDIA/NeMo-Curator/issues/33
        dask.config.set({"dataframe.convert-string": convert_string})

    @batched
    def score_document(self, df: pd.DataFrame) -> pd.Series:
        scores = [[0.5, "EN"], [0.7, "HI"], [0.2, "PT"]]
        scores = scores * len(df)
        scores = scores[: len(df)]
        return pd.Series(scores)

    def keep_document(self, score: pd.Series) -> pd.Series:
        return score[0] >= self._cutoff


class TestClassifierFilters:
    def test_fake_quality_filter(self) -> None:
        dataset = list_to_dataset(["a", "b", "c", "d"], npartitions=1)
        filters = ScoreFilter(FakeQualityFilter())
        filtered_data = filters(dataset)

        expected_indices = [1, 2, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    def test_fake_langid_filter(self) -> None:
        dataset = list_to_dataset(["a", "b", "c", "d"], npartitions=1)
        filters = ScoreFilter(FakeLangId())
        filtered_data = filters(dataset)

        expected_indices = [0, 1, 3]
        expected_data = DocumentDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"

    @pytest.mark.skipif(is_unavailable(comet), reason="Test depends on COMET but it's not installed.")
    def test_comet_qe_filter(self) -> None:
        dataset = two_lists_to_parallel_dataset(
            [
                "This sentence will be translated on the Chinese side.",
                "This sentence will have something irrelevant on the Chinese side.",
            ],
            [
                "这句话在中文一侧会被翻译。",
                "至尊戒，驭众戒；至尊戒，寻众戒；魔戒至尊引众戒，禁锢众戒黑暗中。",  # noqa: RUF001
            ],
            "en",
            "zh",
        )

        from nemo_curator.filters import QualityEstimationFilter
        from nemo_curator.utils.distributed_utils import get_client

        client = get_client(n_workers=1)
        filter_ = QualityEstimationFilter(
            "comet-qe",
            cutoff=-0.25,
            mode="bidi",
            score_type=float,
            metadata_fields=["src_lang", "tgt_lang"],
        )
        filtered_data = filter_(dataset)

        expected_indices = [0]
        expected_data = ParallelDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"
        client.close()

    @pytest.mark.skipif(
        is_unavailable(pymarian),
        reason="Test depends on PyMarian but it's not installed.",
    )
    def test_cometoid_qe_filter(self) -> None:
        dataset = two_lists_to_parallel_dataset(
            [
                "This sentence will be translated on the Chinese side.",
                "This sentence will have something irrelevant on the Chinese side.",
            ],
            [
                "这句话在中文一侧会被翻译。",
                "至尊戒，驭众戒；至尊戒，寻众戒；魔戒至尊引众戒，禁锢众戒黑暗中。",  # noqa: RUF001
            ],
            "en",
            "zh",
        )

        from nemo_curator.filters import QualityEstimationFilter
        from nemo_curator.utils.distributed_utils import get_client

        client = get_client(n_workers=1)
        filter_ = QualityEstimationFilter(
            "cometoid-wmt23",
            cutoff=0.75,
            mode="bidi",
            score_type=float,
            metadata_fields=["src_lang", "tgt_lang"],
        )  # enable GPU by gpu=True
        filtered_data = filter_(dataset)

        expected_indices = [0]
        expected_data = ParallelDataset(dataset.df.loc[expected_indices])
        assert all_equal(expected_data, filtered_data), f"Expected {expected_data} but got {filtered_data}"
        client.close()
