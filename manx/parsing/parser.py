"""Parser defines a common parser interface."""

# Standard library imports
from typing import Any, Generator, Protocol, TextIO


__all__ = ["Parser"]


class Parser(Protocol):
    def parse(self, fp: TextIO) -> Generator[Any, None, None]:
        raise NotImplementedError
