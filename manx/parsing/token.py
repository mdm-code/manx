"""Token defines an implementation of a Token structure."""

# Standard library imports
from dataclasses import dataclass
import enum


@enum.unique
class T(enum.Enum):
    EOF = 0
    REGULAR = 1
    BRACKET = 2
    WHITESPACE = 3
    COMMENT = 4


@dataclass(frozen=True, slots=True)
class Token:
    text: str
    type: T
