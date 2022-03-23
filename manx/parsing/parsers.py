"""Parsers contains code handling data parsing."""

# Standard library imports
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


DICT_SEP = "|"


@dataclass(frozen=True, eq=False)
class DictLine:
    _text_id: str | int
    lexel: str
    grammel: str
    form: str
    _count: str | int

    @property
    def text_id(self) -> int:
        return int(self._text_id)

    @property
    def count(self) -> int:
        return int(self._count)

    @property
    def __dict__(self) -> dict[str, Any]: # type: ignore
        return {
            "text_id": self.text_id,
            "lexel": self.lexel,
            "grammel": self.grammel,
            "form": self.form,
            "count": self.count,
        }

    def __eq__(self: DictLine, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        if self.__dict__ == other.__dict__:
            return True
        return False


def parse_dict_line(line: str, *, sep=DICT_SEP) -> DictLine:
    fields = [f for f in line.split(sep) if f]
    result = DictLine(*fields)
    return result
