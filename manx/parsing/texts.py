"""Text contains the text material parser."""

# Standard library imports
from contextlib import contextmanager
from typing import Generator, TextIO


__all__ = ["Reader"]


class Reader:
    def __init__(self, file: TextIO) -> None:
        self._file = file

    def peek(self, k: int = 1) -> list[str]:
        with seek_back(self._file) as revertable_f:
            return list(revertable_f.read(k))

    def consume(self, k: int) -> list[str]:
        result = list(self._file.read(k))
        return result

    def is_EOF(self) -> bool:
        with seek_back(self._file) as revertable_f:
            if revertable_f.read(1) == "":
                return True
            return False

    def tell(self) -> int:
        return self._file.tell()


@contextmanager
def seek_back(file: TextIO) -> Generator[TextIO, None, None]:
    prev = file.tell()
    try:
        yield file
    finally:
        file.seek(prev)


# TODO: Should handle whitespace and comments
# TODO: peek/consume return tokens instead of character code points
# TODO: the last token is EOFToken to terminate parsing
class Lexer:
    def __init__(self, _: Reader) -> None:
        NotImplementedError

    def peek(self, _: int) -> None:
        raise NotImplementedError

    def consume(self, _: int) -> None:
        raise NotImplementedError

    def is_EOF(self) -> None:
        raise NotImplementedError
