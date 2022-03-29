"""Tests for parsing module."""

# Standard library imports
from io import StringIO

# Third-party library
import pytest

# Local library imports
from manx.parsing import parsers


@pytest.fixture
def dict_file_sample() -> StringIO:
    return StringIO(
        "|163|'bed'|'n<pr'|'BED~'|1||\n"
        "|163|'bethink'|'vpt13{rh}'|'BI-yOUHTE'|1||\n"
        "|163|'bury'|'vps13'|'BURIICTH'|1||\n"
        "|163|'ca:f'|'av{rh}'|'COVE'|1||\n"
        "|163|'come'|'vps13'|'*COMEZ'|1||\n"
        "|163|'dead'|'aj'|'DEYD~'|1||\n"
        "|163|'death'|'n'|'DET'|1||\n"
        "|163|'do'|'vps23'|'DOy'|1||\n"
    )


@pytest.mark.parametrize(
    "instance, want",
    [
        (
            "|68|'witannot'|'vps21-apn'|'NITE'|2||",
            parsers.DictLine(68, "witannot", "vps21-apn", "NITE", 2)
        ),
        (
            "|144|''|'neg-v(>av)'|'NE'|1||",
            parsers.DictLine(144, "", "neg-v(>av)", "NE", 1)
        ),
        (
            "|144|'ewe'|'n'|'*AWE'|1||",
            parsers.DictLine(144, "ewe", "n", "*AWE", 1)
        ),
        (
            "|144|''|'P12N'|'yU'|2||",
            parsers.DictLine(144, "", "P12N", "yU", 2)
        ),
        (
            "|177|'&'|'cj'|'AN'|3||",
            parsers.DictLine(177, "&", "cj", "AN", 3)
        ),
    ]
)
def test_parse_single_dict_line(instance: str, want: parsers.DictLine) -> None:
    func = parsers.DictParser()._parse
    have = func(instance)
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
        func = parsers.DictParser()._parse
        func(instance)


def test_dict_parser(dict_file_sample: StringIO) -> None:
    parser: parsers.Parser = parsers.DictParser()
    result = parser.parse(dict_file_sample)
    assert len(list(result)) == 8
