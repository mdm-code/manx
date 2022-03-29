"""Parsers contains code handling data parsing."""

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generator, TextIO


__all__ = [
    "DictLine",
    "DictParser",
]


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
    def __dict__(self) -> dict[str, Any]:  # type: ignore
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


class Parser(ABC):
    @abstractmethod
    def parse(self, fp: TextIO) -> Generator[Any, None, None]:
        raise NotImplementedError


class DictParser(Parser):
    def __init__(self, sep: str = DICT_SEP) -> None:
        self.sep = sep

    def parse(self, fp: TextIO) -> Generator[DictLine, None, None]:
        for line in fp:
            yield self._parse(line)

    def _parse(self, line: str) -> DictLine:
        fields = [f for f in line.strip().split(self.sep) if f]
        try:
            result = DictLine(*fields)
        except TypeError:
            raise ParsingError(f"unable to parse: {line}")
        return result
