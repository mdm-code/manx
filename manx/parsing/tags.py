"Tags contains source code for tagged material parser."

# Standard library imports
from __future__ import annotations
import enum


EOF = "|"


class TagParsingError(Exception):
    ...


class Prefix(str, enum.Enum):
    place_name = ";"
    personal_name = "'"
    regular = "$"


def is_valid(line: str) -> bool:
    """Valid checks if the line starts with a valid prefix."""
    try:
        Prefix(line[0])
    except (ValueError, IndexError):
        return False
    else:
        return True


def is_regular(line: str) -> bool:
    return line[0] == Prefix.regular.value


def parse_line(line: str) -> list[str]:
    if is_valid(line):
        if is_regular(line):
            # TODO: Change to a filter with call and str | list[str] type check
            line = line[1:]
            line = line.split(" ")[0]
            sline = line.split("/")
            sline = [sline[0]] + sline[1].split("_")
        else:
            line = line[2:]
            sline = ["", "", line]
        return sline
    raise TagParsingError(f"failed to parse: {line}")
