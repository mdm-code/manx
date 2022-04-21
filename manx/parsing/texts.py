"""Text contains the text material parser."""

# Standard library imports
from contextlib import contextmanager
from typing import Callable, Generator, TextIO

# Local library imports
from .token import T, Token
from .word import Word


__all__ = ["TextParser"]


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
            failed = False
            while (l := file.readline()) != "\n":
                if not l:
                    failed = True
                    break

            def _skip_over() -> None:
                """Skip over malformed headers in two files:

                1. layamonAat.txt
                2. layamonAbt.txt
                """
                file.seek(0)
                for _ in range(4):
                    file.readline()
                n = 0
                with seek_back(file) as rev_f:
                    while rev_f.read(1) != "{":
                        n += 1
                file.read(n)

            if failed:
                _skip_over()

        super().__init__(file)


@contextmanager
def seek_back(file: TextIO | Reader) -> Generator[TextIO | Reader, None, None]:
    prev = file.tell()
    try:
        yield file
    finally:
        file.seek(prev)


class Lexer:
    def __init__(self, reader: Reader) -> None:
        self._reader = reader
        self._states: dict[str, Callable[[], Token]] = {
            "DEFAULT": self.default,
            "WHITESPACE": self.whitespace,
            "COMMENT": self.comment,
            "EOF": self.eof,
        }
        self.func = self._states["DEFAULT"]

    def next_token(self) -> Token:
        return self.func()

    def comment(self) -> Token:
        text = ""
        while True:
            if self._reader.is_EOF():
                self.func = self._states["EOF"]
                if text:
                    break
                return self.func()

            match self._reader.peek():
                case "}":
                    text += self._reader.consume()
                    self.func = self._states["DEFAULT"]
                    if text:
                        break
                    return self.func()
                case _:
                    text += self._reader.consume()
        return Token(text=text, type=T.COMMENT)

    def eof(self) -> Token:
        return Token("", T.EOF)

    def whitespace(self) -> Token:
        text = ""
        while True:
            if self._reader.is_EOF():
                self.func = self._states["EOF"]
                if text:
                    break
                return self.func()

            match self._reader.peek():
                case " " | "\n":
                    text += self._reader.consume()
                case "{":
                    self.func = self._states["COMMENT"]
                    if text:
                        break
                    return self.func()
                case _:
                    self.func = self._states["DEFAULT"]
                    if text:
                        break
                    return self.func()
        return Token(text=text, type=T.WHITESPACE)

    def default(self) -> Token:
        text = ""
        while True:
            if self._reader.is_EOF():
                self.func = self._states["EOF"]
                if text:
                    break
                return self.func()

            match self._reader.peek():
                case " " | "\n":
                    self.func = self._states["WHITESPACE"]
                    if text:
                        break
                    return self.func()
                case "{":
                    self.func = self._states["COMMENT"]
                    if text:
                        break
                    return self.func()
                case _:
                    text = text + self._reader.consume()
        return Token(text=text, type=T.REGULAR)

    def peek(self) -> Token:
        with seek_back(self._reader):
            return self.next_token()

    def consume(self) -> Token:
        return self.next_token()

    def is_EOF(self) -> bool:
        if self.peek().type == T.EOF:
            return True
        return False


class TextParser:
    def parse_gen(self, file: TextIO) -> Generator[Word, None, None]:
        """Parse returns a Word object for each word tagged in LAEME."""
        lexer = Lexer(reader=TextReader(file=file, skip_preamble=True))

        while (token := lexer.consume()).type != T.EOF:
            if token.type == T.REGULAR:
                yield Word(token=token)

    def parse(self, file: TextIO) -> list[Word]:
        """Parse version suitable for multiprocessing."""
        return list(self.parse_gen(file))
