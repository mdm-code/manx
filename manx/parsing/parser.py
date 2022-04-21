"""Parser defines a common parser interface."""

# Standard library imports
from abc import ABC, abstractmethod
from typing import Any, Generator, TextIO


class Parser(ABC):
    @abstractmethod
    def parse(self, fp: TextIO) -> Generator[Any, None, None]:
        raise NotImplementedError
