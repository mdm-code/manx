"Tags contains source code for tagged material parser."

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
import enum
import itertools
from typing import Iterable, Generator, Protocol, TextIO, TypeAlias

# Third-party library imports
import numpy as np
from numpy import typing as npt

# Local library imports
from .token import T, Token
from .word import Word


__all__ = ["POS", "TagLine", "TagParser"]


Filterable: TypeAlias = str | list[str]


class TagParsingError(Exception):
    ...


class FilterError(Exception):
    ...


class Prefix(str, enum.Enum):
    place_name = ";"
    personal_name = "'"
    regular = "$"


class POS(enum.Enum):
    Undef = 0
    Noun = 1
    Verb = 2
    Adj = 3
    Adv = 4
    Pron = 5
    Prep = 6
    Conj = 7
    Det = 8
    Num = 9
    Int = 10
    Neg = 11

    @property
    def one_hot_vector(self) -> npt.NDArray[np.uint8]:
        shape = len(type(self))
        vec = np.zeros(shape, dtype=np.uint8)
        np.put(vec, self.value, 1)
        return vec


class POSTagger:
    """POSTagger handles part-of-speech tagging og LAEME.

    The brutally (over-)simplified taxonomy used here is purely practical.
    Given the complexity of the original tagging system, a simpler set of
    features had to be conceived to use part-of-speech information in machine
    learning algorithms.
    """

    @staticmethod
    def infer(grammel: str) -> POS:
        if not grammel:
            return POS.Undef

        match grammel[0]:
            case "n":
                if grammel.startswith("neg"):
                    return POS.Neg
                return POS.Noun
            case "q":
                return POS.Num
            case "v":
                return POS.Verb
            case "c":
                return POS.Conj
            case "A" | "T":
                return POS.Det
            case "P" | "R" | "D":
                match grammel:
                    case "D-cpv":
                        return POS.Det
                return POS.Pron
            # NOTE: `im` infinitive marker before verbs was left out on purpose
            case "i":
                match grammel[1]:
                    case "n":
                        match grammel[2]:
                            case "d":  # indef
                                return POS.Pron
                            case "t":  # int
                                return POS.Int
                        return POS.Undef
                return POS.Undef
            case "a":
                match grammel[1]:
                    case "j":
                        return POS.Adj
                    case "v":
                        return POS.Adv
                return POS.Undef
            case "p":
                match grammel[1]:
                    case "r":
                        return POS.Prep
                return POS.Undef
        return POS.Undef


class TagLine:
    """TagLine represents a single valid line from .TAG corpus file."""

    def __init__(
        self,
        prefix: str,
        lexel: str,
        grammel: str,
        form: str,
    ) -> None:
        self._prefix = prefix
        # NOTE: Carry over grammel to lexel if there is no lexel
        self.lexel = lexel if lexel else grammel
        self.stripped_lexel = self._strip(lexel) if lexel else grammel
        self.grammel = grammel
        self._form = Word(
            Token(
                # NOTE: Only ; and ' are used as prefixes, $ is not
                text=form if prefix == "$" else prefix + form,
                type=T.REGULAR,
            )
        )
        match prefix:
            case "$":
                self.line = f"{prefix}{lexel}/{grammel}_{form}"
            case _:
                self.line = f"{prefix}_{form}"
        self.tagger = POSTagger

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
    def pos(self) -> POS:
        return self.tagger.infer(self.grammel)

    @property
    def prefix(self) -> Prefix:
        return Prefix(self._prefix)

    @property
    def form(self) -> str:
        return self._form.text

    @property
    def stripped_form(self) -> str:
        return self._form.stripped_text

    def _strip(self, lexel: str) -> str:
        if (idx := lexel.find("{")) != -1:
            return lexel[:idx]
        if (idx := lexel.find("[")) != -1:
            return lexel[:idx]
        return lexel


class TagParser:
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


class Filtering(Protocol):
    def __call__(self, data: Filterable) -> Filterable:
        raise NotImplementedError

    def process(self, data: Filterable) -> Filterable:
        raise NotImplementedError


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


class Splitter(Filter, ABC):
    def __init__(self, delim: str | None = None) -> None:
        self.delim = delim


class GetFirst(Splitter):
    "GetFirst gets the first element from a sequence."

    def process(self, data: Filterable) -> Filterable:
        if isinstance(data, list):
            return data[0]
        return data.split(self.delim)[0]


class SplitLine(Splitter):
    "SplitLine splits a line on a predefined delimiter."

    def process(self, data: Filterable) -> Filterable:
        if isinstance(data, list):
            return data
        # NOTE: supply empty missing lexel
        if len((l := data.split(self.delim))) == 1:
            return ["", *l]
        else:
            return l


class AsConstituents(Splitter):
    "AsConstituents resolves a line to the lexel, grammel and form."

    def process(self, data: Filterable) -> Filterable:
        try:
            lexel, grammel, form, *_ = data[0], *data[1].split(self.delim)
        except IndexError:
            raise FilterError(f"failed to split {data}")
        return [lexel, grammel, form]


def filters() -> Generator[Filtering, None, None]:
    """Filters provided an ordered sequence of filters."""
    yield SkipMark()
    yield GetFirst(" ")
    yield SplitLine("/")
    yield AsConstituents("_")


class Pipeline:
    "Pipeline handles applying filters one by one to the input data."

    def __init__(self, filters: Iterable[Filtering] = filters()) -> None:
        self.filters = filters

    def __call__(self, data: Filterable) -> Filterable:
        self.filters, _filters = itertools.tee(self.filters)
        for f in _filters:
            data = f(data)
        return data
