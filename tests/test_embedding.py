"""Tests of word embedding models."""

# Local library imports
from manx import embedding


def test_model_singleton() -> None:
    """Check if two models have the same object ID."""
    m1 = embedding.Model(None)  # type: ignore
    m2 = embedding.Model(None)  # type: ignore
    assert id(m1) == id(m2)

