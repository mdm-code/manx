"""Tests for the nlp package."""

# Standard library imports
from typing import Generator

# Third-party library imports
import pytest

# Local library imports
from manx import parsing
from manx.nlp import text


@pytest.fixture
def parsed() -> Generator[parsing.TagLine, None, None]:
    def _inner():
        yield parsing.TagLine(*["$", "son", "nG", "SUN+ES"])
        yield parsing.TagLine(*["$", "", "P21N", "wE"])
        yield parsing.TagLine(*["$", "be:tan", "vpp", "I+BET"])
    return _inner()


def test_dummy(parsed: Generator[parsing.TagLine, None, None]) -> None:
    label = "tituslang2t"
    words = list(parsed)
    txt = text.Text(label=label, elems=words.copy())
    txt2 = text.Text(label=label, elems=words.copy())
    assert txt.words is not words
    assert txt.label == label
    assert txt != txt2
    assert txt._uuid != txt2._uuid
    assert txt._uuid == txt._uuid
    assert txt.id != txt2.id
    assert txt.id == txt.id
