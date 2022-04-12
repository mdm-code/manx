"Tags contains source code for tagged material parser."

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
import enum


EOF = "|"


class TagParsingError(Exception):
    ...


class Prefix(str, enum.Enum):
    place_name = ";"
    personal_name = "'"
    regular = "$"


def is_valid(line: str) -> bool:
    """Valid checks if the line starts with a valid prefix."""
    try:
        Prefix(line[0])
    except (ValueError, IndexError):
        return False
    else:
        return True


def is_regular(line: str) -> bool:
    return line[0] == Prefix.regular.value


def parse_line(line: str) -> list[str]:
    if is_valid(line):
        if is_regular(line):
            # TODO: Change to a filter with call and str | list[str] type check
            line = line[1:]
            line = line.split(" ")[0]
            sline = line.split("/")
            sline = [sline[0]] + sline[1].split("_")
        else:
            line = line[2:]
            sline = ["", "", line]
        return sline
    raise TagParsingError(f"failed to parse: {line}")


class Filter(ABC):
    def __call__(self, data: str | list[str]) ->  str | list[str]:
        if isinstance(data, str):
            return self.process(data)
        try:
            iter(data)
        except TypeError as e:
            raise e
        else:
            return self.process_iter(data)

    @abstractmethod
    def process(self, _: str) -> str:
        raise NotImplementedError

    def process_iter(self, itr: list[str]) -> list[str]:
        return [self.process(t) for t in itr]
