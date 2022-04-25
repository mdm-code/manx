"""
Doc module contains the representation of a single corpus text for the purpose
of natural language processing.
"""

# Standard library imports
from __future__ import annotations
from typing import Text, TYPE_CHECKING
import uuid

# Local library imports
if TYPE_CHECKING:
    from manx.parsing import TagLine


__all__ = ["ngrams", "Doc", "Span"]


# TODO: Text can represent words as fasttext embedding vectors
# TODO: Text errors out when prebuilt fasttext model does not exist
class Doc:
    """Doc object representing a single LAEME document."""

    def __init__(self, elems: list[TagLine], label: str | None = None) -> None:
        self._label = label if label else ""
        self._elems = elems

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __len__(self) -> int:
        return len(self._elems)

    def __getitem__(self, i: slice | int) -> Span:
        return Span(self.words[i])

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

    def text(self, *, strip: bool = False) -> Text:
        return " ".join(
            [w.stripped_form if strip else w.form for w in self._elems]
        )


class Span:
    """A slice of Doc object."""

    def __init__(self, elems: list[TagLine] | TagLine) -> None:
        if isinstance(elems, list):
            self._elems = elems
        else:
            self._elems = [elems]

    def __len__(self) -> int:
        return len(self._elems)

    def __getitem__(self, i: slice | int) -> TagLine | list[TagLine]:
        return self._elems.copy()[i]


def ngrams(source: Doc, *, n: int = 3) -> list[tuple[TagLine, ...]]:
    result: list[tuple[TagLine, ...]] = list(
        zip(*[source[n:] for n in range(n)])  # type: ignore
    )
    return result
