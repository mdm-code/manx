"Tags contains source code for tagged material parser."

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
import enum
import itertools
from typing import Iterable, Generator, TextIO, TypeAlias

# Local library imports
from .blocks import Parser, T, Token, Word


__all__ = [
    "TagLine",
    "TagParser",
]


Filterable: TypeAlias = str | list[str]


class TagParsingError(Exception):
    ...


class FilterError(Exception):
    ...


class Prefix(str, enum.Enum):
    place_name = ";"
    personal_name = "'"
    regular = "$"


class TagLine:
    """TagLine represents a single valid line from .TAG corpus file."""

    def __init__(
        self, prefix: str, lexel: str, grammel: str, form: str
    ) -> None:
        self._prefix = prefix
        # NOTE: Carry over grammel to lexel if there is no lexel
        self.lexel = lexel if lexel else grammel
        self.grammel = grammel

        # NOTE: Only ; and ' are used as prefixes, $ is not
        form = form if prefix == "$" else prefix + form
        self._form = Word(Token(text=form, type=T.REGULAR))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        try:
            result = True
            for attr in {"prefix", "lexel", "grammel", "form"}:
                if getattr(self, attr) != getattr(other, attr):
                    result = False
                    break
        except AttributeError as e:
            raise e
        else:
            return result

    @property
    def prefix(self) -> Prefix:
        return Prefix(self._prefix)

    @property
    def form(self) -> str:
        return self._form.text

    @property
    def stripped_form(self) -> str:
        return self._form.stripped_text


class TagParser(Parser):
    def parse(self, fp: TextIO) -> Generator[TagLine, None, None]:
        for line in fp:
            try:
                line = line.strip()
                result = self._parse(line)
            except TagParsingError:
                continue
            else:
                yield result

    def _parse(self, line: str) -> TagLine:
        if self._is_valid(line):

            # NOTE: Handle corpus erroneous annotation
            if line == ";_FRAN/CE":
                line = line.replace("/", "\\")

            mark = line[0]
            pipe = Pipeline(filters=filters())
            result = pipe(line)
            result = [mark] + list[str](result)
            return TagLine(*result)
        raise TagParsingError(f"unable to parse: {line}")

    def _is_valid(self, line: str) -> bool:
        """Valid checks if the line starts with a valid prefix."""
        try:
            Prefix(line[0])
        except (ValueError, IndexError):
            return False
        else:
            if line.startswith("'") or line.startswith(";"):
                if line[1] != "_":
                    return False
            return True


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
