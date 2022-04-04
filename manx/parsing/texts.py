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

    def peek(self, k: int = 1) -> str:
        with seek_back(self._file) as revertable_f:
            return revertable_f.read(k)

    def consume(self, k: int) -> str:
        return self._file.read(k)

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


@dataclass(frozen=True, slots=True)
class Token:
    text: str
    type: T


class Lexer:
    def __init__(self, reader: Reader) -> None:
        self._reader = reader
        self._states: dict[str, Callable] = {"default": self.default}
        self.func = self.default

    def next_token(self) -> Token:
        return self.func()

    def default(self) -> Token:
        text = ""
        n = 1
        ws = {"\n", " "}

        if self._reader.is_EOF():
            return Token(text, T.EOF)

        while not self._reader.is_EOF() and self._reader.peek(n) not in ws:
            text = text + self._reader.consume(n)
        else:
            while not self._reader.is_EOF() and self._reader.peek(n) in ws:
                self._reader.consume(n)
        return Token(text, T.REGULAR)

    def peek(self) -> Token:
        with seek_back(self._reader) as _:
            return self.next_token()

    def consume(self) -> Token:
        return self.next_token()

    def is_EOF(self) -> bool:
        if self._reader.is_EOF():
            return True
        return False
