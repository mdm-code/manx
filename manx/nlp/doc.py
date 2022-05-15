"""
Doc module contains the representation of a single corpus text for the purpose
of natural language processing.
"""

# Standard library imports
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Text, TYPE_CHECKING, TypeVar, Protocol
import uuid

# Third-party library imports
import numpy as np

# Local library imports
if TYPE_CHECKING:
    from manx.embedding import Model
    from manx.parsing import POS


__all__ = ["Doc", "ngrams", "Token", "Span"]


@dataclass(slots=True)
class Token:
    lexel: str
    stripped_lexel: str
    grammel: str
    form: str
    stripped_form: str
    _pos: POS
    _model: Model | None = field(repr=False, default=None)
    _embedding: np.ndarray = field(init=False, repr=False)

    @property
    def pos(self) -> str:
        return self._pos.name

    @property
    def embedding(self) -> np.ndarray | None:
        if self._model is None:
            return None
        if not hasattr(self, "_embedding"):
            self._embedding = self._model.get_word_vector(self.form)
        return self._embedding


class Doc:
    """Doc object representing a single LAEME document."""

    def __init__(self, elems: list[Token], label: str | None = None) -> None:
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
    def words(self) -> list[Token]:
        return self._elems.copy()

    def text(self, *, strip: bool = False) -> Text:
        return " ".join(
            [w.stripped_form if strip else w.form for w in self._elems]
        )


class Span:
    """A slice of Doc object."""

    def __init__(self, elems: list[Token] | Token) -> None:
        if isinstance(elems, list):
            self._elems = elems
        else:
            self._elems = [elems]

    def __len__(self) -> int:
        return len(self._elems)

    def __getitem__(self, i: slice | int) -> Token | list[Token]:
        return self._elems.copy()[i]


T = TypeVar("T", covariant=True)


class Sequenced(Protocol[T]):
    def __getitem__(self, i: slice | int) -> T | list[T]:
        raise NotImplementedError


def ngrams(source: Sequenced[Token], *, n: int = 3) -> list[tuple[Token, ...]]:
    result: list[tuple[Token, ...]] = list(
        zip(*[source[n:] for n in range(n)])  # type: ignore
    )
    return result
