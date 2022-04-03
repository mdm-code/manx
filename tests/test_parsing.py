"""Tests for parsing module."""

# Standard library imports
from io import StringIO

# Third-party library
import pytest

# Local library imports
from manx.parsing import dicts, texts


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


@pytest.fixture()
def text_file_sample() -> StringIO:
    return StringIO(
        "# 163\n"
        "{Aberdeen University Library 154, fol. 368v: couplet and 3 quatrains}\n"
        "C13b2-C14a1\n"
        "378 159 N\n"
        "\n\n"
        "{=NE Somerset=}\n"
        "{=Sample represents all the text in English in this hand=}\n"
        "{=Script - semi-cursive Anglicana=}\n"
        "{=Status - MS punctuation done; tagging notes and textual notes up to date=}\n"
        "{~f368v~}\n"
        "{=last folio of MS, containing a couplet in English, some Latin notes and three separate quatrains in English, each having its four lines linked with braces=} {para}YORE WAS A LONDE {.} WRATHE {.} AND *HATE {.} AN HONDE {.} {\\} {=10 lines of Latin=} {para}WANE yE NIyIG HIS DEYD~ {=Stroke through the loop of the back of D=} ME BURIICTH HIM COVE {\\}\n"
        "*COMEZ yE yUNGE STRUPLING AND WOCTH IS LOUE {\\}\n"
        "*HE DRINKET OF HIS GOD ALE AN HET OF HIS LOWE {\\}\n"
        "*AN SINGEZ FOR HIS SOULE GIUELE-GOUE {.} {\\} {para}WAYLAWAY NU HIS ME VO {.} N>O>U ROTYE IHC {=MS ICHC with first C subpuncted=} HUNDER MOLD~ {\\}\n"
        "*MI FRENDES LOUE IS AL AGO {.} FOR DET NE HAUET NO HOLD~ {\"loyalty, allegiance\"} {\\}\n"
        "*HEO BET MINE MESTE FON {.} yAT ME LOUIE SSOLD~ {\\}\n"
        "*HE DRAHET HEM TO {.} AN DOy ME FRO {.} yAT IC [][P]END~ {=first letter lost and second partially lost because of a wormhole=} NOLD~ {\\} {para}*HWO-SO HIM BI-yOUHTE YN-WARD-LICHE AN HO[F]TE {=F partly lost because of a wormhole=} {\\}\n"
        "*HOU HARD IS yE WORE FRUOM BED~ TO y[] {=letter lost in wormhole=} FLORE {\\}\n"
        "*FRr^OUM {=i.e. both R and superscript O which usual implies also preceding <r>=} FLORE TO VULUTTE {=i.e. journey from life to death=} FROM VLUTTE TO PUTTE {\\}\n"
        "*NE SOLDE NEUERE SOENNE MANNES HERTE A-WYNNE {\\}\n"
    )


@pytest.mark.parametrize(
    "instance, want",
    [
        (
            "|68|'witannot'|'vps21-apn'|'NITE'|2||",
            dicts.DictLine(68, "witannot", "vps21-apn", "NITE", 2)
        ),
        (
            "|144|''|'neg-v(>av)'|'NE'|1||",
            dicts.DictLine(144, "", "neg-v(>av)", "NE", 1)
        ),
        (
            "|144|'ewe'|'n'|'*AWE'|1||",
            dicts.DictLine(144, "ewe", "n", "*AWE", 1)
        ),
        (
            "|144|''|'P12N'|'yU'|2||",
            dicts.DictLine(144, "", "P12N", "yU", 2)
        ),
        (
            "|177|'&'|'cj'|'AN'|3||",
            dicts.DictLine(177, "&", "cj", "AN", 3)
        ),
    ]
)
def test_parse_single_dict_line(instance: str, want: dicts.DictLine) -> None:
    func = dicts.DictParser()._parse
    have = func(instance)
    assert have == want


@pytest.mark.parametrize(
    "instance",
    [
        "",
        "|167|&|cj||12||",
        ",177,'&','cj','AN',3,,",
        "|seven|'&'|'cj'|'AN'|3||",
    ]
)
def test_parse_raises_parsing_error(instance: str) -> None:
    with pytest.raises(dicts.ParsingError):
        func = dicts.DictParser()._parse
        func(instance)


def test_dict_parser(dict_file_sample: StringIO) -> None:
    parser: dicts.Parser = dicts.DictParser()
    result = parser.parse(dict_file_sample)
    assert len(list(result)) == 8


@pytest.mark.parametrize("n_chars", [5, 10, 0])
def test_reader_peek(text_file_sample: StringIO, n_chars: int) -> None:
    """Test if the peek() method does not advance the cursor."""
    reader = texts.Reader(text_file_sample)
    prev = reader._file.tell()
    reader.peek(n_chars)
    assert prev == reader.tell() == 0


@pytest.mark.parametrize("n_chars", [10, 20, 300])
def test_reader_consume(text_file_sample: StringIO, n_chars: int) -> None:
    """Assert that consume advances the file cursor."""
    reader = texts.Reader(text_file_sample)
    prev = reader._file.tell()
    reader.consume(n_chars)
    assert reader._file.tell() == prev + n_chars


@pytest.mark.parametrize(
    "n_chars, want",
    [
        (5, False),
        (100_000_000, True),
    ]
)
def test_reader_is_eof(
    text_file_sample: StringIO, n_chars: int, want: bool
) -> None:
    """Test if the EOF is True when the cursor's at the end of the file."""
    reader = texts.Reader(text_file_sample)
    reader._file.read(n_chars)
    have = reader.is_EOF()
    assert have == want
