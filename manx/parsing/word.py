"""
Word defines a Word structure representing the form of a corpus word token.
"""

# Standard library imports
from __future__ import annotations
from typing import TYPE_CHECKING

# Local library imports
if TYPE_CHECKING:
    from .token import Token


__all__ = ["Word"]


class Word:
    """Word is the final outcome of the word form parsing."""

    def __init__(self, token: Token) -> None:
        self._token = token

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self._token.__eq__(other._token)

    @property
    def stripped_text(self) -> str:
        if not hasattr(self, "_text"):
            self._stripped_text = (
                self._token.text.replace("^", "")
                .replace("+", "")
                .replace("-", "")
                .replace("x", "")
                .replace("v", "")
                .replace("*", "")
                .replace("'", "")
                .replace(";", "")
                .replace("!", "")
                .replace("[", "")
                .replace("]", "")
                .replace("\\", "")
                .replace("<", "")
                .replace(">", "")
            )
        return self._stripped_text

    @property
    def text(self) -> str:
        return self._token.text

    def has_superscript(self) -> bool:
        """Superscript text is prefixed with `^`."""
        if self._token.text.find("^") == -1:
            return False
        return True

    def has_separator(self) -> bool:
        """Separators are either `-` or `+`."""
        if self._token.text.find("+") != -1:
            return True
        if self._token.text.find("-") != -1:
            return True
        return False

    def has_diacritics(self) -> bool:
        """Diacritics are either `v` or `x`."""
        if self._token.text.find("v") != -1:
            return True
        elif self._token.text.find("x") != -1:
            return True
        return False

    def is_capital(self) -> bool:
        "Capital letters are prefixed with `*`."
        if self._token.text.find("*") == -1:
            return False
        return True

    def is_personal_name(self) -> bool:
        "Personal names are prefixed with `'`."
        if self._token.text.find("'") == -1:
            return False
        return True

    def is_place_name(self) -> bool:
        "Place names are prefixed with `;`."
        if self._token.text.find(";") == -1:
            return False
        return True

    def is_miscellaneous(self) -> bool:
        """Miscellanea are prefixed with `!`."""
        if self._token.text.find("!") == -1:
            return False
        return True

    def has_gaps(self) -> bool:
        """Gaps are marked with [].

        They can be stripped regardless of whether there are characters inside
        square brackets or not. In case there are, it means that they were
        legible enough to include them.
        """
        if self._token.text.find("[") == -1:
            return False
        return True

    def has_line_end(self) -> bool:
        """End of the line is marked with backward slash."""
        if self._token.text.find("\\") == -1:
            return False
        return True

    def has_deletion(self) -> bool:
        """Deletions left for tagging are placedd between `<` characters."""
        if self._token.text.find("<") == -1:
            return False
        return True

    def has_insertions(self) -> bool:
        """Insertions left for tagging are placedd between `>` characters."""
        if self._token.text.find(">") == -1:
            return False
        return True
