"""Tests for the nlp package."""

# Standard library imports
from io import StringIO

# Third-party library imports
import pytest

# Local library imports
from manx import parsing
from manx.nlp import tokens
from .test_parsing import tag_file_sample


@pytest.fixture
def parsed() -> list[parsing.TagLine]:
    def _inner():
        yield parsing.TagLine(*["$", "son", "nG", "SUN+ES"])
        yield parsing.TagLine(*["$", "", "P21N", "wE"])
        yield parsing.TagLine(*["$", "be:tan", "vpp", "I+BET"])
    return list(_inner())


def test_doc_words_immutable(parsed: list[parsing.TagLine]) -> None:
    """Verify if words are returned as a copy upon each call."""
    label = "tituslang2t"
    t = tokens.doc(parsed, label=label)
    assert t.tokens is not t.tokens


def test_doc_is_iterable(parsed: list[parsing.TagLine]) -> None:
    """Verify that Doc object is iterable."""
    _ = [_ for _ in tokens.doc(parsed)]


def test_doc_equality(parsed: list[parsing.TagLine]) -> None:
    """Each Doc object is assigned a unique UUID used in equality check."""
    t1 = tokens.doc(parsed)
    t2 = tokens.doc(parsed)
    assert t1 != t2


def test_doc_iteration(parsed: list[parsing.TagLine]) -> None:
    """Each Doc object is assigned a unique UUID used in equality check."""
    t1 = tokens.doc(parsed)
    t2 = tokens.doc(parsed)
    assert t1 != t2


@pytest.mark.parametrize(
    "strip, want",
    [
        (False, "SUN+ES wE I+BET"),
        (True, "SUNES wE IBET"),
    ]
)
def test_doc_output(
    parsed: list[parsing.TagLine], strip: bool, want: str
) -> None:
    """Verify regular and stripped text output."""
    t = tokens.doc(parsed, label="tituslang2t")
    assert t.text(strip=strip) == want


@pytest.mark.parametrize(
    "s, length",
    [
        (slice(0,10), 10),
        (slice(10,20), 10),
        (slice(5,10,3), 2),
        (slice(0, 24), 24),
        (slice(0, 24, 2), 12),
    ]
)
def test_doc_getitem(
    tag_file_sample: StringIO, s: slice, length: int
) -> None:
    parser = parsing.TagParser()
    d = tokens.doc(list(parser.parse(tag_file_sample)))
    span = d[s]
    assert len(span) == length


@pytest.mark.integration
@pytest.mark.parametrize(
    "n, want",
    [
        (3, 22),
        (4, 21),
        (5, 20),
    ]
)
def test_ngrams(n: int, want: int, tag_file_sample: StringIO) -> None:
    """Check if the output ngram list has the expected length."""
    parser = parsing.TagParser()
    d = tokens.doc(list(parser.parse(tag_file_sample)))
    ngrms = tokens.ngrams(d[:], n=n)
    assert len(ngrms) == want
