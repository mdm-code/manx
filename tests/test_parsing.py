"""Tests for parsing module."""

# Standard library imports
from io import StringIO, SEEK_END, SEEK_CUR
from typing import Any, Callable

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
        "\n"
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


def test_reader_with_seek_back() -> None:
    reader = texts.Reader(StringIO(""))
    with texts.seek_back(reader) as r:
        r.read()


def test_reader_preamble_error() -> None:
    with pytest.raises(texts.PreambleReadingError):
        _ = texts.TextReader(StringIO(""))


def test_lexer_output_short() -> None:
    text = StringIO("*COMEZ yE yUNGE STRUPLING AND WOCTH IS LOUE {\\}\n")
    want = [
        texts.Token("*COMEZ", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("yE", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("yUNGE", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("STRUPLING", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("AND", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("WOCTH", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("IS", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("LOUE", texts.T.REGULAR),
        texts.Token(" ", texts.T.WHITESPACE),
        texts.Token("{\\}", texts.T.COMMENT),
        texts.Token("\n", texts.T.WHITESPACE),
        texts.Token("", texts.T.EOF),
    ]
    reader = texts.Reader(text)
    lexer = texts.Lexer(reader)
    for word in want:
        assert lexer.consume() == word


def test_lexer_unterminated_comment() -> None:
    reader = texts.Reader(StringIO("{=NE Somerset="))
    lexer = texts.Lexer(reader)
    assert lexer.next_token() == texts.Token("{=NE Somerset=", texts.T.COMMENT)


def test_lexer_full_text_pass(text_file_sample: StringIO) -> None:
    reader = texts.TextReader(text_file_sample)
    lexer = texts.Lexer(reader)
    while lexer.next_token().type != texts.T.EOF:
        pass


def test_preamble_skipping(text_file_sample: StringIO) -> None:
    reader = texts.TextReader(text_file_sample, skip_preamble=True)
    lexer = texts.Lexer(reader)
    assert lexer.next_token() == texts.Token("{=NE Somerset=}", texts.T.COMMENT)


@pytest.mark.parametrize(
    "instance, want",
    [
        (SEEK_END, True),
        (SEEK_CUR, False),
    ]
)
def test_lexer_is_eof(
    text_file_sample: StringIO, instance: int, want: bool
) -> None:
    reader = texts.TextReader(text_file_sample)
    lexer = texts.Lexer(reader)
    reader.seek(0, instance)
    assert lexer.is_EOF() == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (texts.Word(texts.Token("*COMEZ", texts.T.REGULAR)), "COMEZ"),
        (texts.Word(texts.Token("'yUNGE", texts.T.REGULAR)), "yUNGE"),
        (texts.Word(texts.Token("STRUP>L>ING", texts.T.REGULAR)), "STRUPLING"),
        (texts.Word(texts.Token("!WOCTH", texts.T.REGULAR)), "WOCTH"),
        (texts.Word(texts.Token(";LOUE", texts.T.REGULAR)), "LOUE"),
        (texts.Word(texts.Token("BI-yENCH", texts.T.REGULAR)), "BIyENCH"),
        (texts.Word(texts.Token("*I+NE", texts.T.REGULAR)), "INE"),
        (texts.Word(texts.Token("Tr^OWIS", texts.T.REGULAR)), "TrOWIS"),
        (texts.Word(texts.Token("HAF\\LES", texts.T.REGULAR)), "HAFLES"),
        (texts.Word(texts.Token("LI[V]", texts.T.REGULAR)), "LIV"),
        (texts.Word(texts.Token("ER<y<E", texts.T.REGULAR)), "ERyE"),
        (texts.Word(texts.Token("Fr^A", texts.T.REGULAR)), "FrA"),
        (texts.Word(texts.Token("MIvKEL", texts.T.REGULAR)), "MIKEL"),
        (texts.Word(texts.Token("SUILxK", texts.T.REGULAR)), "SUILK"),
    ]
)
def test_word_stripped_text(instance: texts.Word, want: str) -> None:
    """Check whether the stripped text matches the expected form."""
    assert instance.stripped_text == want


@pytest.mark.parametrize(
    "instance, func, want",
    [
        (
            texts.Word(texts.Token("*COMEZ", texts.T.REGULAR)),
            texts.Word.is_capital,
            True
        ),
        (
            texts.Word(texts.Token("COMEZ", texts.T.REGULAR)),
            texts.Word.is_capital,
            False
        ),
        (
            texts.Word(texts.Token("'yUNGE", texts.T.REGULAR)),
            texts.Word.is_personal_name,
            True
        ),
        (
            texts.Word(texts.Token("yUNGE", texts.T.REGULAR)),
            texts.Word.is_personal_name,
            False
        ),
        (
            texts.Word(texts.Token("STRUP>L>ING", texts.T.REGULAR)),
            texts.Word.has_insertions,
            True
        ),
        (
            texts.Word(texts.Token("STRUPLING", texts.T.REGULAR)),
            texts.Word.has_insertions,
            False
        ),
        (
            texts.Word(texts.Token("!WOCTH", texts.T.REGULAR)),
            texts.Word.is_miscellaneous,
            True,
        ),
        (
            texts.Word(texts.Token("WOCTH", texts.T.REGULAR)),
            texts.Word.is_miscellaneous,
            False,
        ),
        (
            texts.Word(texts.Token(";LOUE", texts.T.REGULAR)),
            texts.Word.is_place_name,
            True,
        ),
        (
            texts.Word(texts.Token("LOUE", texts.T.REGULAR)),
            texts.Word.is_place_name,
            False,
        ),
        (
            texts.Word(texts.Token("BI-yENCH", texts.T.REGULAR)),
            texts.Word.has_separator,
            True,
        ),
        (
            texts.Word(texts.Token("BIyENCH", texts.T.REGULAR)),
            texts.Word.has_separator,
            False,
        ),
        (
            texts.Word(texts.Token("*I+NE", texts.T.REGULAR)),
            texts.Word.has_separator,
            True,
        ),
        (
            texts.Word(texts.Token("*INE", texts.T.REGULAR)),
            texts.Word.has_separator,
            False,
        ),
        (
            texts.Word(texts.Token("Tr^OWIS", texts.T.REGULAR)),
            texts.Word.has_superscript,
            True,
        ),
        (
            texts.Word(texts.Token("TrOWIS", texts.T.REGULAR)),
            texts.Word.has_superscript,
            False,
        ),
        (
            texts.Word(texts.Token("HAF\\LES", texts.T.REGULAR)),
            texts.Word.has_line_end,
            True,
        ),
        (
            texts.Word(texts.Token("HAFLES", texts.T.REGULAR)),
            texts.Word.has_line_end,
            False,
        ),
        (
            texts.Word(texts.Token("LI[V]", texts.T.REGULAR)),
            texts.Word.has_gaps,
            True,
        ),
        (
            texts.Word(texts.Token("LIV", texts.T.REGULAR)),
            texts.Word.has_gaps,
            False,
        ),
        (
            texts.Word(texts.Token("ER<y<E", texts.T.REGULAR)),
            texts.Word.has_deletion,
            True,
        ),
        (
            texts.Word(texts.Token("ERyE", texts.T.REGULAR)),
            texts.Word.has_deletion,
            False,
        ),
        (
            texts.Word(texts.Token("Fr^A", texts.T.REGULAR)),
            texts.Word.has_superscript,
            True
        ),
        (
            texts.Word(texts.Token("FrA", texts.T.REGULAR)),
            texts.Word.has_superscript,
            False
        ),
        (
            texts.Word(texts.Token("MIvKEL", texts.T.REGULAR)),
            texts.Word.has_diacritics,
            True,
        ),
        (
            texts.Word(texts.Token("MIKEL", texts.T.REGULAR)),
            texts.Word.has_diacritics,
            False,
        ),
        (
            texts.Word(texts.Token("SUILxK", texts.T.REGULAR)),
            texts.Word.has_diacritics,
            True,
        ),
        (
            texts.Word(texts.Token("SUILK", texts.T.REGULAR)),
            texts.Word.has_diacritics,
            False,
        ),
    ]
)
def test_word_checks(
    instance: texts.Word, func: Callable[[texts.Word], bool], want: bool
) -> None:
    """Check whether the stripped text matches the expected form."""
    assert func(instance) == want


def test_word_equality() -> None:
    """Words with the equal underlying token are equal."""
    word_one = texts.Word(texts.Token("BI-yENCH", texts.T.REGULAR))
    word_two =texts.Word(texts.Token("BI-yENCH", texts.T.REGULAR))
    assert word_one == word_two


@pytest.mark.parametrize(
    "instance, want",
    [
        (object, False),
        (texts.Word(texts.Token("&LONGE", texts.T.REGULAR)), False),
    ]
)
def test_word_inequality(instance: Any, want: bool) -> None:
    ref = texts.Word(texts.Token("TrOWIS", texts.T.REGULAR))
    assert (ref == instance) == want


def test_word_original_token_text() -> None:
    word = texts.Word(texts.Token("BI-yENCH", texts.T.REGULAR))
    assert word.text == "BI-yENCH"
