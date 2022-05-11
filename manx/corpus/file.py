"""File exposes shared corpus file implementation."""

# Standard library imports
from __future__ import annotations
import enum
import io
import os
from typing import Protocol, TYPE_CHECKING

# Local library imports
if TYPE_CHECKING:
    from .fs import Dir


__all__ = ["FileType"]


class FileType(enum.Enum):
    Unidentified = 0
    Text = 1
    Dict = 2
    Html = 3
    Tags = 4


class Contents(Protocol):
    @property
    def text(self) -> str:
        raise NotImplementedError


class CorpusFile:
    """CorpusFile represents a corpus text file from LAEME."""

    def __init__(self, name: str, contents: Contents) -> None:
        self.name = name
        self.contents = contents

    @property
    def text(self) -> str:
        return self.contents.text

    @property
    def stem(self) -> str:
        return self.name.split(".")[0]

    def as_io(self) -> io.StringIO:
        return io.StringIO(self.contents.text)

    @property
    def type(self) -> FileType:
        if hasattr(self, "_type"):
            return self._type
        self._type: FileType = self._eval_type()
        return self._type

    def _eval_type(self) -> FileType:
        try:
            stem, *_, ext = self.name.split(".")
        except ValueError:
            stem, ext = "", ""
        match ext.lower():
            case "tag":
                return FileType.Tags
            case "html":
                return FileType.Html
            case "txt":
                if stem.split("_")[-1] == "mysql":
                    return FileType.Dict
                return FileType.Text
            case _:
                return FileType.Unidentified

    def save(self, node: Dir) -> None:
        with open(os.path.join(node.path, self.name), "w") as fout:
            fout.write(self.text)
