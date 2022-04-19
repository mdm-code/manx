"""Parsing module handles LAEME corpus file parsing."""

# Local library imports
from .dicts import *
from .tags import *
from .texts import *


__all__ = dicts.__all__ + tags.__all__ + texts.__all__  # type: ignore
