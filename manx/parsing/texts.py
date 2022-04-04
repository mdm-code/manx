"""Text contains the text material parser."""

# Standard library imports
from contextlib import contextmanager
from dataclasses import dataclass
import enum
from typing import Callable, Generator, TextIO


__all__ = ["Lexer", "Reader"]


class Reader:
    def __init__(self, file: TextIO) -> None:
        self._file = file

    def peek(self, n: int = 1) -> str:
        with seek_back(self._file) as revertable_f:
            return revertable_f.read(n)

    def consume(self, n: int = 1) -> str:
        return self._file.read(n)

    def is_EOF(self) -> bool:
        with seek_back(self._file) as revertable_f:
            if revertable_f.read(1) == "":
                return True
            return False

    def read(self, n: int = -1) -> str:
        return self._file.read(n)

    def tell(self) -> int:
        return self._file.tell()

    def seek(self, offset: int, whence: int = 0) -> int:
        return self._file.seek(offset, whence)


class TextReader(Reader):
    def __init__(self, file: TextIO, *, skip_preamble: bool = True) -> None:
        """TextReader can skip over the LAEME text file preamble."""
        if skip_preamble:
            while file.readline() != "\n":
                continue
        super().__init__(file)


@contextmanager
def seek_back(file: TextIO | Reader) -> Generator[TextIO | Reader, None, None]:
    prev = file.tell()
    try:
        yield file
    finally:
        file.seek(prev)


@enum.unique
class T(enum.Enum):
    EOF = 0
    REGULAR = 1
    BRACKET = 2
    WHITESPACE = 3


@dataclass(frozen=True, slots=True)
class Token:
    text: str
    type: T


class Lexer:
    def __init__(self, reader: Reader) -> None:
        self._reader = reader
        self._states: dict[str, Callable] = {
            "DEFAULT": self.default,
            "WHITESPACE": self.whitespace,
            "EOF": self.eof,
        }
        self.func = self._states["DEFAULT"]

    def next_token(self) -> Token:
        return self.func()

    # TODO: Implement comment parsing
    def comment(self) -> Token:
        return Token("", T.EOF)

    def eof(self) -> Token:
        return Token("", T.EOF)

    def whitespace(self) -> Token:
        text = ""

        while True:
            if self._reader.is_EOF():
                self.func = self._states["EOF"]
                if text:
                    return Token(text, T.REGULAR)
                return Token(text, T.EOF)

            match self._reader.peek():
                case " " | "\n":
                    text += self._reader.consume()
                # case "{":
                #     continue
                case _:
                    self.func = self._states["DEFAULT"]
                    return Token(text=text, type=T.WHITESPACE)

    def default(self) -> Token:
        text = ""

        while True:
            if self._reader.is_EOF():
                self.func = self._states["EOF"]
                if text:
                    return Token(text, T.REGULAR)
                return Token(text, T.EOF)

            match self._reader.peek():
                case " " | "\n":
                    self.func = self._states["WHITESPACE"]
                    return Token(text=text, type=T.REGULAR)
                # case "{":
                #     continue
                case _:
                    text = text + self._reader.consume()

    def peek(self) -> Token:
        with seek_back(self._reader) as _:
            return self.next_token()

    def consume(self) -> Token:
        return self.next_token()

    def is_EOF(self) -> bool:
        if self._reader.is_EOF():
            return True
        return False
