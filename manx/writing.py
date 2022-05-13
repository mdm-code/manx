"""Write controls the output of manx parse command."""

# Standard library imports
from __future__ import annotations
import enum
from typing import TextIO, TYPE_CHECKING

# Local library imports
if TYPE_CHECKING:
    from manx import nlp


__all__ = ["Format", "write"]


class WriteFormatError(Exception):
    ...


class Format(str, enum.Enum):
    FullText = "full"
    StripText = "strip"
    # TODO: Write out parsed corpus to JSON for use with jq
    JSON = "json"


def write(
    fp: TextIO, docs: list[nlp.Doc], fmt: Format = Format.StripText
) -> None:
    """Write out corpus contents to target file in a given format."""
    match fmt:
        case Format.FullText:
            lines = [d.text(strip=False) + "\n" for d in docs]
            fp.writelines(lines)
        case Format.StripText:
            lines = [d.text(strip=True) + "\n" for d in docs]
            fp.writelines(lines)
        case _:
            raise WriteFormatError(f"{fmt} is not supported")
