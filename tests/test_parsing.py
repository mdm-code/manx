"""Tests for parsing module."""

# Third-party library
import pytest

# Local library imports
from manx.parsing import parsers


@pytest.mark.parametrize(
    "case, want",
    [
        (
            "|68|'witannot'|'vps21-apn'|'NITE'|2||",
            parsers.DictLine(68, "'witannot'", "'vps21-apn'", "'NITE'", 2)
        ),
        (
            "|144|''|'neg-v(>av)'|'NE'|1||",
            parsers.DictLine(144, "''", "'neg-v(>av)'", "'NE'", 1)
        ),
        (
            "|144|'ewe'|'n'|'*AWE'|1||",
            parsers.DictLine(144, "'ewe'", "'n'", "'*AWE'", 1)
        ),
        (
            "|144|''|'P12N'|'yU'|2||",
            parsers.DictLine(144, "''", "'P12N'", "'yU'", 2)
        ),
        (
            "|177|'&'|'cj'|'AN'|3||",
            parsers.DictLine(177, "'&'", "'cj'", "'AN'", 3)
        ),
    ]
)
def test_parse_single_dict_line(
    case: str, want: parsers.DictLine
) -> None:
    have = parsers.parse_dict_line(case)
    # reveal_type(want)
    assert have == want
