"""Tests for parsing module."""

# Third-party library
import pytest

# Local library imports
from manx.parsing import parsers


@pytest.mark.parametrize(
    "instance, want",
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
def test_parse_single_dict_line(instance: str, want: parsers.DictLine) -> None:
    have = parsers.parse_dict_line(instance)
    assert have == want


@pytest.mark.parametrize(
    "instance",
    [
        "",
        "|167|&|cj||12||",
        ",177,'&','cj','AN',3,,",
    ]
)
def test_parse_raises_parsing_error(instance: str) -> None:
    with pytest.raises(parsers.ParsingError):
        parsers.parse_dict_line(instance)
