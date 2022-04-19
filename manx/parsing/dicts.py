"""Parsers contains code handling data parsing."""

# Standard library imports
from __future__ import annotations
from dataclasses import dataclass
from typing import Generator, TextIO

# Local library imports
from .parser import Parser


__all__ = [
    "DictLine",
    "DictParser",
]


DICT_SEP = "|"

N_FIELDS = 5


class ParsingError(Exception):
    ...


@dataclass(frozen=True, slots=True)
class DictLine:
    text_id: int
    lexel: str
    grammel: str
    form: str
    count: int


class DictParser(Parser):
    def __init__(self, sep: str = DICT_SEP, n_fields: int = N_FIELDS) -> None:
        self.sep = sep
        self.n_fields = n_fields

    def parse(self, fp: TextIO) -> Generator[DictLine, None, None]:
        for line in fp:
            yield self._parse(line)

    def _parse(self, line: str) -> DictLine:
        fields = [f for f in line.strip().split(self.sep) if f]

        if (l := len(fields)) != self.n_fields:
            raise ParsingError(f"expected {self.n_fields}; got {l}")

        def _strip(field: str) -> str:
            return field.strip("'")

        try:
            result = DictLine(
                text_id=int(fields[0]),
                lexel=_strip(fields[1]),
                grammel=_strip(fields[2]),
                form=_strip(fields[3]),
                count=int(fields[4]),
            )
        except (TypeError, ValueError):
            raise ParsingError(f"unable to parse: {line}")
        return result
