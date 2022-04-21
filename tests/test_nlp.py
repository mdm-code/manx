"""Tests for the nlp package."""

# Third-party library imports
import pytest

# Local library imports
from manx import parsing
from manx.nlp import text


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
    t = text.Text(label, parsed)
    assert t.words is not t.words


def test_text_id_uniqueness(parsed: list[parsing.TagLine]) -> None:
    """Check if IDs differ for two different objects."""
    t1 = text.Text("", parsed)
    t2 = text.Text("", parsed)
    assert t1.id != t2.id


def test_text_equality(parsed: list[parsing.TagLine]) -> None:
    """Each Text object is assigned a unique UUID used in equality check."""
    t1 = text.Text("", parsed)
    t2 = text.Text("", parsed)
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
    t = text.Text("tituslang2t", parsed)
    assert t.text(strip=strip) == want
