"""
Tokens module contains building blocks of a single corpus text for the purpose
of natural language processing.
"""

# Standard library imports
from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Generic, Text, TYPE_CHECKING, TypeVar, Protocol
import uuid

# Third-party library imports
import numpy as np

# Local library imports
if TYPE_CHECKING:
    from manx.embedding import Model
    from manx.parsing import POS, TagLine


__all__ = ["doc", "Doc", "ngrams", "Token", "Span"]


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

    def __len__(self) -> int:
        return 1

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


def doc(
    elems: list[TagLine], model: Model | None = None, label: str | None = None
) -> Doc:
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
                _pos=e.pos,
                _model=model,
            )
            for e in elems
        ],
    )
    return result


class Doc:
    """Doc object representing a single LAEME text."""

    def __init__(self, elems: list[Token], label: str | None = None) -> None:
        self._label = label if label else ""
        self._elems = elems

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.id == other.id

    def __len__(self) -> int:
        return len(self._elems)

    def __getitem__(self, i: slice | int) -> Token | Span[Token]:
        if isinstance(i, int):
            return deepcopy(self.tokens[i])
        else:
            return Span[Token](self.tokens[i])

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
    def tokens(self) -> list[Token]:
        return self._elems.copy()

    def text(self, *, strip: bool = False) -> Text:
        return " ".join(
            [w.stripped_form if strip else w.form for w in self._elems]
        )


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
            return deepcopy(self._elems[i])
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
