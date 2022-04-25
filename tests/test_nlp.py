"""Tests for the nlp package."""

# Standard library imports
from io import StringIO

# Third-party library imports
import pytest

# Local library imports
from manx import parsing
from manx.nlp import doc
from .test_parsing import tag_file_sample


@pytest.fixture
def parsed() -> list[parsing.TagLine]:
    def _inner():
        yield parsing.TagLine(*["$", "son", "nG", "SUN+ES"])
        yield parsing.TagLine(*["$", "", "P21N", "wE"])
        yield parsing.TagLine(*["$", "be:tan", "vpp", "I+BET"])
    return list(_inner())


def test_text_words_immutable(parsed: list[parsing.TagLine]) -> None:
    """Verify if words are returned as a copy upon each call."""
    label = "tituslang2t"
    t = doc.Doc(label, parsed)
    assert t.words is not t.words


def test_text_id_uniqueness(parsed: list[parsing.TagLine]) -> None:
    """Check if IDs differ for two different objects."""
    t1 = doc.Doc("", parsed)
    t2 = doc.Doc("", parsed)
    assert t1.id != t2.id


def test_text_equality(parsed: list[parsing.TagLine]) -> None:
    """Each Doc object is assigned a unique UUID used in equality check."""
    t1 = doc.Doc("", parsed)
    t2 = doc.Doc("", parsed)
    assert t1 != t2

@pytest.mark.parametrize(
    "strip, want",
    [
        (False, "SUN+ES wE I+BET"),
        (True, "SUNES wE IBET"),
    ]
)
def test_text_output(
    parsed: list[parsing.TagLine], strip: bool, want: str
) -> None:
    """Verify regular and stripped text output."""
    t = doc.Doc("tituslang2t", parsed)
    assert t.text(strip=strip) == want


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
    txt = doc.Doc("", list(parser.parse(tag_file_sample)))
    ngrms = doc.ngrams(txt, n=n)
    assert len(ngrms) == want
