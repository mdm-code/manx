"""Parsing module handles LAEME corpus file parsing."""

# Local library imports
from .dicts import *
from .tags import *
from .texts import *
from .word import *
from .parser import *


__all__ = (
    dicts.__all__  # type: ignore
    + tags.__all__  # type: ignore
    + texts.__all__  # type: ignore
    + word.__all__  # type: ignore
    + parser.__all__  # type: ignore
)
