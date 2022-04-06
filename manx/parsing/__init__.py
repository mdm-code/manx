"""Parsing module handles ELALME file parsing."""

# Local library imports
from .dicts import *
from .texts import *

__all__ = dicts.__all__ + texts.__all__  # type: ignore
