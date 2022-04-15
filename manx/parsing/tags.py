"Tags contains source code for tagged material parser."

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
import enum
import itertools
from typing import Iterable, Generator, TypeAlias


EOF = "|"


Filterable: TypeAlias = str | list[str]


class TagParsingError(Exception):
    ...


class FilterError(Exception):
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


def parse_line(line: str) -> Filterable:
    if is_valid(line):
        pipe = Pipeline(filters=filters())
        result = pipe(line)
        return result
    raise TagParsingError(f"failed to parse: {line}")


class Filter(ABC):
    def __call__(self, data: Filterable) -> Filterable:
        return self.process(data)

    @abstractmethod
    def process(self, data: Filterable) -> Filterable:
        raise NotImplementedError


class SkipMark(Filter):
    "SkipMark skips the first element in a sequence."
    def process(self, data: Filterable) -> Filterable:
        return data[1:]


class Splitter(Filter):
    def __init__(self, delim: str | None = None) -> None:
        self.delim = delim


class GetFirst(Splitter):
    "GetFirst gets the first element from a sequence."
    def process(self, line: Filterable) -> Filterable:
        if isinstance(line, list):
            return line[0]
        return line.split(self.delim)[0]


class SplitLine(Splitter):
    "SplitLine splits a line on a predefined delimiter."
    def process(self, line: Filterable) -> Filterable:
        if isinstance(line, list):
            return line
        # NOTE: supply empty missing lexel
        if len((l := line.split(self.delim))) == 1:
            return ["", *l]
        else:
            return l


class AsConstituents(Splitter):
    "AsConstituents resolves a line to the lexel, grammel and form."
    def process(self, line: Filterable) -> Filterable:
        try:
            lexel, grammel, form, *_ = line[0], *line[1].split(self.delim)
        except IndexError:
            raise FilterError(f"failed to split {line}")
        return [lexel, grammel, form]


def filters() -> Generator[Filter, None, None]:
    """Filters provided an ordered sequence of filters."""
    yield SkipMark()
    yield GetFirst(" ")
    yield SplitLine("/")
    yield AsConstituents("_")


class Pipeline:
    "Pipeline handles applying filters one by one to the input data."
    def __init__(self, filters: Iterable[Filter] = filters()) -> None:
        self.filters = filters

    def __call__(self, data: Filterable) -> Filterable:
        self.filters, _filters = itertools.tee(self.filters)
        for f in _filters:
            data = f(data)
        return data
