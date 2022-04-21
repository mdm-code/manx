"""
Text module contains the representation of a single corpus text for the purpose
of natural language processing.
"""

# Standard library imports
from __future__ import annotations
from typing import TYPE_CHECKING
import uuid

# Local library imports
if TYPE_CHECKING:
    from manx.parsing import TagLine

"""
TODO:
    1. Text is able to be turned to ngrams
    2. Text is able to be turned to POS vector
    3. Text is able to represent word as fasttext embedding vector
    6. Text exposes its content for persistence
"""


class Text:
    def __init__(self, label: str, elems: list[TagLine]) -> None:
        self._label = label
        self._elems = elems

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    @property
    def label(self) -> str:
        return self._label

    @property
    def id(self) -> str:
        if hasattr(self, "_uuid"):
            return self._uuid.hex
        self._uuid: uuid.UUID = uuid.uuid4()
        return self._uuid.hex

    @property
    def words(self) -> list[TagLine]:
        return self._elems.copy()
