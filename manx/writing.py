"""Write controls the output of manx parse command."""

# Standard library imports
from __future__ import annotations
import enum
import json
from typing import Text, TextIO, TYPE_CHECKING

# Local library imports
if TYPE_CHECKING:
    from manx import nlp


__all__ = ["Format", "write"]


class WriteFormatError(Exception):
    ...


class Format(str, enum.Enum):
    FullText = "full"
    StripText = "strip"
    JSONLines = "jsonlines"


def marshall_output(docs: list[nlp.Doc], fmt: Format) -> Text:
    match fmt:
        case Format.FullText:
            result = "\n".join(d.text(strip=False) for d in docs)
        case Format.StripText:
            result = "\n".join(d.text(strip=True) for d in docs)
        case Format.JSONLines:
            result = json.dumps([d.asdict() for d in docs])
        case _:
            raise WriteFormatError(f"{fmt.value} formatting is not supported")
    return result


def write(
    fp: TextIO, docs: list[nlp.Doc], fmt: Format = Format.StripText
) -> int:
    """Write out corpus contents to target file in a given format."""
    output = marshall_output(docs, fmt)
    return fp.write(output)
