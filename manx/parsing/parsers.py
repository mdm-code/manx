"""Parsers contains code handling data parsing."""

# Standard library imports
from __future__ import annotations
from dataclasses import dataclass


DICT_SEP = "|"


class ParsingError(Exception):
    ...


@dataclass(frozen=True, eq=False)
class DictLine:
    _text_id: str | int
    _lexel: str
    _grammel: str
    _form: str
    _count: str | int

    @property
    def text_id(self) -> int:
        return int(self._text_id)

    @property
    def count(self) -> int:
        return int(self._count)

    @property
    def lexel(self) -> str:
        return self._strip(self._lexel)

    @property
    def grammel(self) -> str:
        return self._strip(self._grammel)

    @property
    def form(self) -> str:
        return self._strip(self._form)

    @property
    def __dict__(self) -> dict[str, str | int]: # type: ignore
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

    def _strip(self, s: str) -> str:
        return s.strip("'")


def parse_dict_line(line: str, *, sep: str = DICT_SEP) -> DictLine:
    fields = [f for f in line.split(sep) if f]
    try:
        result = DictLine(*fields)
    except TypeError:
        raise ParsingError(f"unable to parse: {line}")
    return result
