"""
Tokens module contains building blocks of a single corpus text for the purpose
of natural language processing.
"""

# Standard library imports
from __future__ import annotations
from copy import copy
from dataclasses import dataclass, field
from typing import Generic, Text, TypeAlias, TYPE_CHECKING, TypeVar, Protocol
import uuid

# Third-party library imports
import numpy as np
from numpy import typing as npt

# Local library imports
if TYPE_CHECKING:
    from manx.parsing import POS, TagLine


__all__ = ["doc", "Doc", "ngrams", "Token", "Span"]


TokenDict: TypeAlias = dict[str, str | int]

DocDict: TypeAlias = dict[str, str | int | list[TokenDict]]


@dataclass(slots=True)
class Token:
    lexel: str
    stripped_lexel: str
    grammel: str
    form: str
    stripped_form: str
    sequence: int
    _pos: POS
    _uuid: uuid.UUID = field(init=False, repr=False)

    def __len__(self) -> int:
        return 1

    @property
    def pos(self) -> str:
        return self._pos.name

    @property
    def one_hot_pos_vector(self) -> npt.NDArray[np.uint8]:
        return self._pos.one_hot_vector

    @property
    def id(self) -> str:
        if not hasattr(self, "_uuid"):
            self._uuid: uuid.UUID = uuid.uuid4()
        return self._uuid.hex

    def asdict(self) -> TokenDict:
        result: TokenDict = {
            "id": self.id,
            "lexel": self.lexel,
            "stripped_lexel": self.stripped_lexel,
            "grammel": self.grammel,
            "form": self.form,
            "stripped_form": self.stripped_form,
            "sequence": self.sequence,
            "pos": self.pos,
        }
        return result


def doc(elems: list[TagLine], label: str | None = None) -> Doc:
    """Assemble Doc object representing a single LAEME text."""
    result = Doc(
        label=label,
        elems=[
            Token(
                lexel=e.lexel,
                stripped_lexel=e.stripped_lexel,
                grammel=e.grammel,
                form=e.form,
                stripped_form=e.stripped_form,
                sequence=i,
                _pos=e.pos,
            )
            for i, e in enumerate(elems, start=0)
        ],
    )
    return result


class Doc:
    """Doc object representing a single LAEME text."""

    def __init__(self, elems: list[Token], label: str | None = None) -> None:
        self._label = label if label else ""
        self._elems = elems
        self._cur = 0

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __len__(self) -> int:
        return len(self._elems)

    def __iter__(self) -> Doc:
        return self

    def __next__(self) -> Token:
        try:
            result = copy(self._elems[self._cur])
        except IndexError:
            self._cur = 0
            raise StopIteration
        else:
            self._cur += 1
            return result

    def __getitem__(self, i: slice | int) -> Token | Span[Token]:
        if isinstance(i, int):
            return copy(self.tokens[i])
        else:
            return Span[Token](self.tokens[i])

    @property
    def label(self) -> str:
        return self._label

    @property
    def id(self) -> str:
        if not hasattr(self, "_uuid"):
            self._uuid: uuid.UUID = uuid.uuid4()
        return self._uuid.hex

    @property
    def tokens(self) -> list[Token]:
        return self._elems.copy()

    def text(self, *, strip: bool = False) -> Text:
        return " ".join(
            [w.stripped_form if strip else w.form for w in self._elems]
        )

    def asdict(self) -> DocDict:
        result: DocDict = {
            "id": self.id,
            "label": self.label,
            "length": len(self),
            "tokens": [t.asdict() for t in self._elems],
        }
        return result


T = TypeVar("T", covariant=True)


class Span(Generic[T]):
    """A slice of Doc object."""

    def __init__(self, elems: T | list[T]) -> None:
        if isinstance(elems, list):
            self._elems = elems
        else:
            self._elems = [elems]

    def __len__(self) -> int:
        return len(self._elems)

    def __getitem__(self, i: slice | int) -> T | Span[T]:
        if isinstance(i, int):
            return copy(self._elems[i])
        else:
            return Span[T](self._elems.copy()[i])


class Sequenced(Protocol[T]):
    def __len__(self) -> int:
        raise NotImplementedError

    def __getitem__(self, i: slice | int) -> T | Span[T]:
        raise NotImplementedError


def ngrams(
    source: Token | Sequenced[Token], *, n: int = 3
) -> list[tuple[Token, ...]]:
    if isinstance(source, Token):
        if n == 1:
            return [(source,)]
        else:
            return []
    result: list[tuple[Token, ...]] = list(
        zip(*[source[n:] for n in range(n)])  # type: ignore
    )
    return result
