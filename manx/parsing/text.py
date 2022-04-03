"""Text contains the text material parser."""

# Standard library imports
from typing import TextIO


# TODO: Create a Tokenizer class iterating over an open file buffer
# TODO: peek/consume could emit list[str] with N steps
# TODO: remember about .seek(X) method on opened TextIO (and StringIO)
class Reader:
    def __init__(self, file: TextIO) -> None:
        self.file = file

    def peek(self, k: int = 1) -> list[str]:
        result: list[str] = []

        # TODO: Turn it into a context manager
        prev = self.file.tell()

        for c in self.file.read(k):
            result.append(c)

        self.file.seek(prev)

        return result

    def consume(self, _: int) -> None:
        raise NotImplementedError

    def isEOF(self) -> None:
        raise NotImplementedError


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

    def isEOF(self) -> None:
        raise NotImplementedError
