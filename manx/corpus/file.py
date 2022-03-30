"""File handles ordering and saving files on the local file system."""

# Standard library imports
from __future__ import annotations
import enum
import os
from pathlib import Path
from typing import TYPE_CHECKING

# Local library imports
if TYPE_CHECKING:
    from .download import Saver


__all__ = ["Dir", "DirName", "traverse"]


class DirName(str, enum.Enum):
    texts = "texts"
    dicts = "dicts"

    @classmethod
    @property
    def members(cls) -> set[str]:
        return set(cls.__members__.keys())

    @classmethod
    def is_valid(cls, s: str) -> bool:
        return s in cls.members  # type: ignore


class Dir:
    """Dir represents a directory node in the file system."""

    def __init__(
        self, name: str, files: list[Saver], parent: Dir | None = None
    ) -> None:
        self.name = name
        self.parent = parent
        self.files: list[Saver] = files
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


def from_dir(root: str) -> None:
    """from_dir reconstructs the corpus directory structure in memory."""
    if not os.path.isdir(root):
        raise Exception

    for d in filter(
        lambda x: x.is_dir(),
        (Path(os.path.join(root, p)) for p in os.listdir(root)),
    ):
        if DirName.is_valid(d.name):
            files = list(
                filter(
                    lambda x: x.is_file(),
                    (d.joinpath(p) for p in os.listdir(d)),
                )
            )
            pass


def traverse(node: Dir) -> None:
    """Traverse directory structure creating directories and files."""
    if not os.path.isdir(node.path):
        os.mkdir(node.path)
    for f in node.files:
        f.save(node)
    for child in node.children:
        traverse(child)
