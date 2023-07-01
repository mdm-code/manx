"""Fs handles ordering and saving files on the local file system."""

# Standard library imports
from __future__ import annotations
from dataclasses import dataclass
import enum
from functools import wraps
import os
from pathlib import Path
from typing import Callable

# Local library imports
from .file import CorpusFile


__all__ = ["Dir", "DirName", "from_root", "traverse"]


class DirName(str, enum.Enum):
    texts = "texts"
    dicts = "dicts"
    tags = "tags"

    @property
    @classmethod
    def members(cls) -> set[str]:
        return set(cls.__members__.keys())

    @classmethod
    def is_valid(cls, s: str) -> bool:
        return s in cls.members  # type: ignore


class Dir:
    """Dir represents a directory node in the file system."""

    def __init__(
        self, name: str, files: list[CorpusFile], parent: Dir | None = None
    ) -> None:
        self.name = name
        self.parent = parent
        self.files: list[CorpusFile] = files
        self.children: list[Dir] = []

    @property
    def path(self) -> str:
        parent = self.parent
        path_elems = [self.name]
        while parent:
            path_elems.append(parent.name)
            parent = parent.parent
        else:
            path_elems.reverse()
            self._path = os.path.join(*path_elems)
        return self._path

    def __truediv__(self: Dir, other: Dir) -> Dir:
        return self.join(other)

    def join(self: Dir, other: Dir) -> Dir:
        if not isinstance(other, type(self)):
            raise TypeError
        other.parent = self
        self.children.append(other)
        return other


@dataclass(slots=True, frozen=True)
class FileContents:
    text: str


def files(func: Callable[[str], Dir]) -> Callable[[str], list[CorpusFile]]:
    @wraps(func)
    def wrapped(*args: str, **kwargs: str):
        d = func(*args, **kwargs)
        result: list[CorpusFile] = []
        for subdir in d.children:
            result.extend(subdir.files)
        return result

    return wrapped


@files
def from_root(root: str) -> Dir:
    """from_root reconstructs the corpus directory structure in memory."""
    if not os.path.isdir(root):
        raise ValueError

    directory = Dir(root, files=[])

    def _read(fn: os.PathLike) -> FileContents:
        with open(fn) as f:
            result = FileContents(text=f.read())
        return result

    for d in filter(
        lambda x: x.is_dir(),
        (Path(os.path.join(root, p)) for p in os.listdir(root)),
    ):
        if DirName.is_valid(d.name):
            subdir = directory / Dir(d.name, files=[])
            files = list(
                filter(
                    lambda x: x.is_file(),
                    (d.joinpath(p) for p in os.listdir(d)),
                )
            )
            corpus_files = [CorpusFile(f.name, _read(f)) for f in files]
            subdir.files.extend(corpus_files)
    return directory


def traverse(node: Dir) -> None:
    """Traverse directory structure creating directories and files."""
    if not os.path.isdir(node.path):
        os.mkdir(node.path)
    for f in node.files:
        f.save(node)
    for child in node.children:
        traverse(child)
