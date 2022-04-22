"""
Text module contains the representation of a single corpus text for the purpose
of natural language processing.
"""

# Standard library imports
from __future__ import annotations
import typing
import uuid

# Local library imports
if typing.TYPE_CHECKING:
    from manx.parsing import TagLine


# TODO: Text can represent words as fasttext embedding vectors
# TODO: Text errors out when prebuilt fasttext model does not exist
# TODO: nlp.load(from_web: bool = True) is made available
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

    def text(self, *, strip: bool = False) -> typing.Text:
        return " ".join(
            [w.stripped_form if strip else w.form for w in self._elems]
        )


def ngrams(source: Text, *, n: int = 3) -> list[tuple[TagLine, ...]]:
    result = list(zip(*[source.words[n:] for n in range(n)]))
    return result
