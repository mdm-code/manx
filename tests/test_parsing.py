"""Tests for parsing module."""

# Standard library imports
from io import StringIO, SEEK_END, SEEK_CUR
from typing import Any, Callable

# Third-party library
import numpy as np
from numpy import typing as npt
import pytest

# Local library imports
from manx.parsing import dicts, texts, tags, parser, prons


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


@pytest.fixture()
def tag_file_sample() -> StringIO:
    return StringIO(
        "{~f246v~}\n"
        "$whenso/cj>=_*HwENNE-SO $so/cj-k_-SO\n"
        "{=Two-line initial *H with the ascender extending two further lines up\n"
        "in the left margin=}\n"
        "$will/n_WIL\n"
        "$wit/nOd_wIT\n"
        "$oversti:gan/vps13{rh}_OFER-STI+Ed $over-/xp-v_OFER- $/vps13[V]{rh}_+Ed\n"
        "{.}\n"
        "{\\}\n"
        "$then/av<=_*yENNE\n"
        "$be/vps13_IS\n"
        "$will/n_WIL\n"
        "$&/cj_AND\n"
        "$wit/n_WIT\n"
        "$forlose/vSpp{rh}_FOR-LOR+E $for-/xp-v_FOR- $/vSpp[R]{rh}_+E\n"
        "{.}\n"
        "{\\}\n"
        "$whenso/cj_*HwENNE-SO $so/cj-k_-SO\n"
        "$will/n_wIL\n"
        "$/P13GM_HIS\n"
        "$heat/nOd_HETE\n"
        "$hie/vps13K2{rh}_HI+Ed $/vps13[V]K2{rh}_+Ed\n"
        "{.}\n"
        "{\\}\n"
        "$there/av_*yER\n"
        "$benot/vps13_N+IS $n-/xp-neg>=_N+\n"
        "$not/neg-v<=_NOwIHT\n"
        "$wit/n_WIT\n"
        "$choose/vSpp{rh}_I+COR+E $ge-/xp-vpp_I+ $/vSpp[R]{rh}_+E\n"
        "{.}\n"
        "{\\}\n"
        "$often/av_*OFTE\n"
        "$will/n_WIL\n"
        "$to/pr_TO\n"
        "$sorrow/n<pr_SEORzE\n"
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
    p: parser.Parser = dicts.DictParser()
    result = p.parse(dict_file_sample)
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


def test_preamble_skipping_2() -> None:
    sample = StringIO(
        "# 278\n"
        "{London, British Library,\n"
        "7-26vb (foot); 27ra line 6 (end): Layamon A}\n"
        "C13b1\n"
        "381 271 N {N Worcs=}"
    )
    reader = texts.TextReader(sample)
    lexer = texts.Lexer(reader)
    assert lexer.consume() == texts.Token(
        text="{N Worcs=}", type=texts.T.COMMENT
    )


@pytest.mark.parametrize(
    "instance, want",
    [
        ("{>)(*LIBER *OCTAUUS()>}", False),
        ("$son/nG_SUN+ES $/Gn_+ES", True),
        ("$&/cj_&", True),
        ("'_*IAMES", True),
        (";_ENGLELOND", True),
        ("", False),
        ("Tolkien (1962) are often not visible on the film=}", False),
        ("# 272", False),
        ("C13b?", False),
        ("C13b-14a", False),
        ("352 275 N", False),
    ]
)
def test_tags_line_valid(instance: str, want: bool) -> None:
    parser = tags.TagParser()
    assert parser._is_valid(instance) == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (
            "$son/nG_SUN+ES $/Gn_+ES",
            tags.TagLine(*["$", "son", "nG", "SUN+ES"]),
        ),
        (
            "$&/cj_&",
            tags.TagLine(*["$", "and", "cj", "&"]),
        ),
        (
            "$/P21N_wE",
            tags.TagLine(*["$", "", "P21N", "wE"]),
        ),
        (
            "$thank{g}/nOd_yONC",
            tags.TagLine(*["$", "thank{g}", "nOd", "yONC"]),
        ),
        (
            "$be:tan/vpp_I+BET $ge-/xp-vpp_I+",
            tags.TagLine(*["$", "be:tan", "vpp", "I+BET"]),
        ),
        (
            "'_*IAMES",
            tags.TagLine(*["'", "", "", "*IAMES"]),
        ),
        (
            ";_ENGLELOND",
            tags.TagLine(*[";", "", "", "ENGLELOND"]),
        ),
    ]
)
def test_tag_line_parsing(instance: str, want: bool) -> None:
    parser = tags.TagParser()
    assert parser._parse(instance) == want


@pytest.mark.parametrize(
    "instance, want",
    [
        ("'_*IAMES", "_*IAMES"),
        ("$son/nG_SUN+ES $/Gn_+ES", "son/nG_SUN+ES $/Gn_+ES"),
        ("$be:tan/vpp_I+BET $ge-/xp-vpp_I+", "be:tan/vpp_I+BET $ge-/xp-vpp_I+"),
    ]
)
def test_skip_mark(instance: str, want: str) -> None:
    has = tags.SkipMark().process(instance)
    assert has == want


@pytest.mark.parametrize(
    "instance, want",
    [
        ("_*IAMES", "_*IAMES"),
        ("son/nG_SUN+ES $/Gn_+ES", "son/nG_SUN+ES"),
        ("be:tan/vpp_I+BET $ge-/xp-vpp_I+", "be:tan/vpp_I+BET"),
        (["be:tan/vpp_I+BET", "$ge-/xp-vpp_I+"], "be:tan/vpp_I+BET"),
    ]
)
def test_get_first(instance: str, want: str) -> None:
    has = tags.GetFirst(" ").process(instance)
    assert has == want


@pytest.mark.parametrize(
    "instance, want",
    [
        ("_*IAMES", ["", "_*IAMES"]),
        ("son/nG_SUN+ES", ["son", "nG_SUN+ES"]),
        ("be:tan/vpp_I+BET", ["be:tan", "vpp_I+BET"]),
        ("/P21N_wE", ["", "P21N_wE"]),
        ("thank{g}/nOd_yONC", ["thank{g}", "nOd_yONC"]),
        (["", "P21N_wE"], ["", "P21N_wE"]),
    ]
)
def test_split_line(instance: str, want: str) -> None:
    has = tags.SplitLine("/").process(instance)
    assert has == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (["", "_*IAMES"], ["", "", "*IAMES"]),
        (["son", "nG_SUN+ES"], ["son", "nG", "SUN+ES"]),
        (["be:tan", "vpp_I+BET"], ["be:tan", "vpp", "I+BET"]),
        (["", "P21N_wE"], ["", "P21N", "wE"]),
        (["thank{g}", "nOd_yONC"], ["thank{g}", "nOd", "yONC"]),
    ]
)
def test_as_constituents(instance: list[str], want: list[str]) -> None:
    has = tags.AsConstituents("_").process(instance)
    assert has == want


@pytest.mark.parametrize(
    "instance, want",
    [
        ("$son/nG_SUN+ES $/Gn_+ES", ["son", "nG", "SUN+ES"]),
        ("$&/cj_&", ["&", "cj", "&"]),
        ("$/P21N_wE", ["", "P21N", "wE"]),
        ("$thank{g}/nOd_yONC", ["thank{g}", "nOd", "yONC"]),
        ("$be:tan/vpp_I+BET $ge-/xp-vpp_I+", ["be:tan", "vpp", "I+BET"]),
        ("'_*IAMES", ["", "", "*IAMES"]),
        (";_ENGLELOND", ["", "", "ENGLELOND"]),
    ]
)
def test_filter_pipeline(instance: str, want: list[str]) -> None:
    pipe = tags.Pipeline(tags.filters())
    has = pipe(instance)
    assert has == want


@pytest.mark.parametrize(
    "instance",
    [
        "{~f246v~}\n",
        "{=Two-line initial *H with ascender extending two further lines up\n",
        "{.}\n",
        "{\\}\n",
    ]
)
def test_tag_parse_raises_parsing_error(instance: str) -> None:
    with pytest.raises(tags.TagParsingError):
        func = tags.TagParser()._parse
        func(instance)


def test_tag_parser(tag_file_sample: StringIO) -> None:
    p: parser.Parser = tags.TagParser()
    result = p.parse(tag_file_sample)
    assert len(list(result)) == 24


@pytest.mark.parametrize(
    "lexel, pos",
    [
        ("nOd", tags.POS.Noun),
        ("nOi", tags.POS.Noun),
        ("n<pr", tags.POS.Noun),
        ("n<pr", tags.POS.Noun),
        ("n<pr-k", tags.POS.Noun),
        ("n<pr-t", tags.POS.Noun),
        ("n-voc", tags.POS.Noun),
        ("n-av", tags.POS.Noun),
        ("nG", tags.POS.Noun),
        ("npl", tags.POS.Noun),
        ("naj", tags.POS.Noun),
        ("n-t", tags.POS.Noun),
        ("P11N", tags.POS.Pron),
        ("P22Oi", tags.POS.Pron),
        ("P12G", tags.POS.Pron),
        ("P21GD", tags.POS.Pron),
        ("P02Oi", tags.POS.Pron),
        ("P13GF", tags.POS.Pron),
        ("P23OdX", tags.POS.Pron),
        ("P13MXM", tags.POS.Pron),
        ("indef", tags.POS.Pron),
        ("A<pr", tags.POS.Det),
        ("TN", tags.POS.Det),
        ("TOd-ad", tags.POS.Det),
        ("TOd-as", tags.POS.Det),
        ("D-cpv", tags.POS.Det),
        ("Dis<pr-ad", tags.POS.Pron),
        ("DespnOd", tags.POS.Pron),
        ("DospnRTAplOi", tags.POS.Pron),
        ("RTIpl", tags.POS.Pron),
        ("RTA<=", tags.POS.Pron),
        ("RT", tags.POS.Pron),
        ("qcG", tags.POS.Num),
        ("qoaj<pr", tags.POS.Num),
        ("qoaj<pr-k", tags.POS.Num),
        ("aj", tags.POS.Adj),
        ("aj{rh}", tags.POS.Adj),
        ("ajOd", tags.POS.Adj),
        ("ajpl<pr{rh}", tags.POS.Adj),
        ("ajnplOd{rh}", tags.POS.Adj),
        ("ajpl-cpv", tags.POS.Adj),
        ("vps13-ct", tags.POS.Verb),
        ("vps23F-apn", tags.POS.Verb),
        ("vps13-ptform", tags.POS.Verb),
        ("vps11", tags.POS.Verb),
        ("vps11Fir", tags.POS.Verb),
        ("vpt13K2", tags.POS.Verb),
        ("vsjps23", tags.POS.Verb),
        ("vSpt12", tags.POS.Verb),
        ("v-imp22", tags.POS.Verb),
        ("vi{rh}", tags.POS.Verb),
        ("vi-m", tags.POS.Verb),
        ("vi-imp", tags.POS.Verb),
        ("vnFier{rh}", tags.POS.Verb),
        ("av", tags.POS.Adv),
        ("av-cpv", tags.POS.Adv),
        ("av-sup", tags.POS.Adv),
        ("av>=", tags.POS.Adv),
        ("av-k", tags.POS.Adv),
        ("pr", tags.POS.Prep),
        ("pr<", tags.POS.Prep),
        ("pr+T", tags.POS.Prep),
        ("int", tags.POS.Int),
        ("cj", tags.POS.Conj),
        ("cj>=", tags.POS.Conj),
        ("cj<=", tags.POS.Conj),
        ("neg-v", tags.POS.Neg),
    ]
)
def test_pos_tagging(lexel: str, pos: tags.POS) -> None:
    assert tags.POSTagger.infer(lexel) == pos


@pytest.mark.parametrize(
    "lexel, want",
    [
        ("in{p}", "in"),
        ("about{re}", "about"),
        ("therein{p}", "therein"),
        ("therein", "therein"),
        ("full{v}", "full"),
        ("ha:tan{c}", "ha:tan"),
        ("nor[neg]", "nor"),
        ("nor[or]", "nor"),
        ("A<pr", "A"),
        ("cj>=", "cj"),
        ("P11N+H", "P11N"),
        ("neg-v", "neg"),
        ("P11G-covpl+C", "P11G"),
    ]
)
def test_lexel_simplification(lexel: str, want: str) -> None:
    assert tags.TagLine("$", lexel, "", "").stripped_lexel == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (tags.TagLine(*["$", "son", "nG", "SUN+ES"]), tags.POS.Noun),
        (tags.TagLine(*["$", "", "P21N", "wE"]), tags.POS.Pron),
        (tags.TagLine(*["$", "be:tan", "vpp", "I+BET"]), tags.POS.Verb),
    ]
)
def test_tag_pos_inference(instance: tags.TagLine, want: tags.POS) -> None:
    assert instance.pos == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (
            tags.TagLine(*["$", "son", "nG", "SUN+ES"]),
            "$son/nG_SUN+ES",
        ),
        (
            tags.TagLine(*["$", "&", "cj", "&"]),
            "$&/cj_&",
        ),
        (
            tags.TagLine(*["$", "", "P21N", "wE"]),
            "$/P21N_wE",
        ),
        (
            tags.TagLine(*["$", "thank{g}", "nOd", "yONC"]),
            "$thank{g}/nOd_yONC",
        ),
        (
            tags.TagLine(*["$", "be:tan", "vpp", "I+BET"]),
            "$be:tan/vpp_I+BET",
        ),
        (
            tags.TagLine(*["'", "", "", "*IAMES"]),
            "'_*IAMES",
        ),
        (
            tags.TagLine(*[";", "", "", "ENGLELOND"]),
            ";_ENGLELOND",
        ),
    ]
)
def test_format_tag_as_line(instance: tags.TagLine, want: bool) -> None:
    assert instance.line == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (
            tags.TagLine(*["$", "", "P21N", "wE"]),
            "P21N",
        ),
        (
            tags.TagLine(*["$", "thank{g}", "nOd", "yONC"]),
            "thank{g}",
        ),
        (
            tags.TagLine(*["$", "be:tan", "vpp", "I+BET"]),
            "be:tan",
        ),
        (
            tags.TagLine(*["'", "", "", "*IAMES"]),
            "***",
        ),
        (
            tags.TagLine(*[";", "", "", "ENGLELOND"]),
            "***",
        ),
        (
            tags.TagLine(*["$", "", "A<pr", "A"]),
            "an",
        ),
        (
            tags.TagLine(*["$", "", "TN", "dE"]),
            "the",
        ),
        (
            tags.TagLine(*["$", "&", "cj", "&"]),
            "and",
        ),
        (
            tags.TagLine(*["$", "", "TOd-ad", "TE"]),
            "the",
        ),
        (
            tags.TagLine(*["$", "", "D-cpv", "yE"]),
            "the",
        ),
    ]
)
def test_proper_place_name_lemma(instance: tags.TagLine, want: str) -> None:
    assert instance.lexel == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (
            tags.POS.Noun,
            np.array(
                [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8
            )
        ),
        (
            tags.POS.Int,
            np.array(
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], dtype=np.uint8
            )
        ),
        (
            tags.POS.Undef,
            np.array(
                [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8
            )
        ),
        (
            tags.POS.Pron,
            np.array(
                [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0], dtype=np.uint8
            )
        ),
        (
            tags.POS.Verb,
            np.array(
                [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=np.uint8
            )
        ),
    ]
)
def test_pos_enum_one_hot_encoding(
    instance: tags.POS, want: npt.NDArray[np.uint8]
) -> None:
    assert np.array_equal(instance.one_hot_vector, want)


@pytest.mark.parametrize(
    "instance, want",
    [
        ("P01<pr{rh}", "P01<pr"),
        ("P11G-av+C", "P11G-av"),
        ("P23G-voc<{rh}+C", "P23G"),
        ("P02G-av+C{rh}", "P02G-av"),
        ("P13GMpnplOd", "P13GMOd"),
        ("P13GMpnplOd{rh}", "P13GMOd"),
        ("P12-voc-ad", "P12"),
        ("P01<pr<{rh}", "P01<pr"),
        ("P12Gint+C", "P12G"),
        ("P13GI-Gn", "P13GI"),
        ("P21<pr>", "P21<pr"),
        ("P12GOdpl-as<", "P12GOd"),
        ("P13<prM>=", "P13<prM"),
        ("P23N>={rh}", "P23N"),
    ]
)
def test_pronoun_pruning(instance: str, want: str) -> None:
    pruner = prons.Pruner()
    have = pruner.prune(instance)
    assert have == want


@pytest.mark.parametrize(
    "instance, want",
    [
        (("P01>pr", "VS"), "us"),
        (("P01<pr", "US"), "us"),
        (("P01X", "VSSELUEN"), "usself"),
        (("P01Oi", "US"), "us"),
        (("P01Od", "VS"), "us"),
        (("P01N", "WE"), "we"),
        (("P01G", "VRE"), "our"),
        (("P02<pr", "YOU"), "you"),
        (("P02>pr", "YOU"), "you"),
        (("P02Od", "zOU"), "you"),
        (("P02Oi", "zU"), "you"),
        (("P02OdX", "EOV"), "you"),
        (("P02G", "OWER"), "your"),
        (("P02N", "YE"), "you"),
        (("P11<pr", "ME"), "me"),
        (("P11>pr{rh}", "ME"), "me"),
        (("P11>pr", "ME"), "me"),
        (("P11G+H", "MY"), "my"),
        (("P11G-voc+C", "MIn"), "mine"),
        (("P11G-av+C", "MI"), "my"),
        (("P11G-voc<{rh}", "MINE"), "mine"),
        (("P11G<prpl+C", "MYNE"), "mine"),
        (("P11G<pr", "MI"), "my"),
        (("P11GG+V", "MINES"), "mine"),
        (("P11GN<{rh}", "MI"), "my"),
        (("P11GOdpl+H", "MYn"), "mine"),
        (("P11N", "IK~"), "I"),
        (("P11N{rh}", "HI"), "I"),
        (("P11N+V{rh}", "I"), "I"),
        (("P11Oi", "MI"), "me"),
        (("P11Od{rh}", "ME"), "me"),
        (("P11Oi<{rh}", "ME"), "me"),
        (("P11<pr+ward", "MEWARD"), "meward"),
        (("P11NX", "ICSULF"), "meself"),
        (("P11<prX", "ME"), "me"),
        (("P11<prX", "MESELUEn"), "meself"),
        (("P11GX", "MINESSULUES"), "meself"),
        (("P11MX", "ME"), "me"),
        (("P11MX<{rh}", "ME"), "me"),
        (("P11OdX{rh}", "ME"), "me"),
        (("P11X", "MISULF"), "meself"),
        (("P11OiX", "ESULFUm"), "meself"),
        (("P11OdX{rh}", "ME"), "me"),
        (("P12-voc", "dU"), "thou"),
        (("P12<pr", "y~E"), "thee"),
        (("P12<pr-ad", "TE"), "thee"),
        (("P12>pr-ad", "TE"), "thee"),
        (("P12G<pr+C", "dIN"), "thine"),
        (("P12G<pr+H", "yI"), "thy"),
        (("P12G<prpl+H", "THI"), "thy"),
        (("P12G<prpl+H", "dINE"), "thine"),
        (("P12GG+C", "yY"), "thy"),
        (("P12GN-ad+H", "TIn"), "thine"),
        (("P12GOd+C", "dInNE"), "thine"),
        (("P12GOd+C", "dY"), "thy"),
        (("P12Gint+V", "yIN"), "thine"),
        (("P12Gpnpl<pr{rh}", "yINE"), "thine"),
        (("P12N", "TU"), "thou"),
        (("P12N-ad{rh}", "TU"), "thou"),
        (("P12Od", "dIE"), "thee"),
        (("P12Od-as{rh}", "TE"), "thee"),
        (("P12Od-ad", "TE"), "thee"),
        (("P12Oi-as{rh}", "TE"), "thee"),
        (("P12Oi", "y~"), "thee"),
        (("P12<prX", "yESELUEN"), "theeself"),
        (("P12<prX{rh}", "yE"), "thee"),
        (("P12GX", "yINESSULFES"), "theeself"),
        (("P12MX", "YE"), "thee"),
        (("P12MX-ad", "TE"), "thee"),
        (("P12OdX", "TESELF"), "theeself"),
        (("P12OdX{rh}", "YE"), "thee"),
        (("P12OiX-ad", "TE"), "thee"),
        (("P12X", "yESULF"), "theeself"),
        (("P12X", "dE"), "thee"),
        (("P12X-ad", "TESELLFENN"), "theeself"),
        (("P12NX", "yOUSELF"), "theeself"),
        (("P12-av", "yE"), "thee"),
        (("P12<pr+ward", "dEwARD"), "theeward"),
        (("P12OiX+ward", "yEWARD"), "theeward"),
        (("P21<pr", "OUS"), "us"),
        (("P21>pr{rh}", "VS"), "us"),
        (("P21Od", "Vus"), "us"),
        (("P21Oi", "HOUS"), "us"),
        (("P21Oi{rh}", "US"), "us"),
        (("P21N", "HUUE"), "we"),
        (("P21N>=", "wE"), "we"),
        (("P21N{rh}", "WE"), "we"),
        (("P21G", "OwER"), "our"),
        (("P21Gpn<pr", "OURIS"), "our"),
        (("P21GpnOd", "OURE"), "our"),
        (("P21Gpnpl", "URE"), "our"),
        (("P21G-voc", "HVRE"), "our"),
        (("P21<prX", "USSELLFENN"), "usself"),
        (("P21<prX", "US"), "us"),
        (("P21MX", "USSELwEN"), "usself"),
        (("P21MX{rh}", "US"), "us"),
        (("P21NX", "wESELUE"), "usself"),
        (("P21OiX", "VS"), "us"),
        (("P21X", "VSSULUE"), "usself"),
        (("P21OdX", "OUS"), "us"),
        (("P21GD", "VNK~"), "unker"),
        (("P21GDpn", "VNC"), "unk"),
        (("P21ND", "wITT"), "wit"),
        (("P21OdD", "VNC"), "unk"),
        (("P21OiD", "HUNKE"), "unk"),
        (("P21OdDX", "UNC"), "unk"),
        (("P21<prD", "UNC"), "unk"),
        (("P21>prD", "UNC"), "unk"),
        (("P22G", "YOURE"), "your"),
        (("P22Gpn{rh}", "YOURES"), "your"),
        (("P22Gpn", "gEURE"), "your"),
        (("P22GpnOd", "YOURE"), "your"),
        (("P22Gpn<pr", "OwRES"), "your"),
        (("P22-voc", "yE"), "you"),
        (("P22N", "zEE"), "you"),
        (("P22N", "YE"), "you"),
        (("P22N{rh}", "zE"), "you"),
        (("P22<pr", "zOW"), "you"),
        (("P22>pr", "EOW"), "you"),
        (("P22Oi", "YOU"), "you"),
        (("P22Oi{rh}", "GIU"), "you"),
        (("P22Od{rh}", "YOU"), "you"),
        (("P22Od", "COw"), "you"),
        (("P22OdDX", "INCSELUEN"), "inkself"),
        (("P22<prD", "gINC"), "ink"),
        (("P22>prDX", "gUNG"), "ink"),
        (("P22GD", "gINKER"), "inker"),
        (("P22GDpn", "InCER"), "inker"),
        (("P22GD", "InC"), "ink"),
        (("P22OdD", "INC"), "ink"),
        (("P22OiD", "HInC"), "ink"),
        (("P22ND", "zET"), "git"),
        (("P22<prX", "gIUSELUEN"), "youself"),
        (("P22>prX", "gUw"), "you"),
        (("P22X", "OUSELF"), "youself"),
        (("P22X", "Ow"), "you"),
        (("P22OdX{rh}", "GIU"), "you"),
        (("P22NX", "zESEOLF"), "youself"),
        (("P22MX", "EOUSELUEN"), "youself"),
        (("P22Gpn-avX", "gUw"), "you"),
        (("P23G", "HEIRE"), "their"),
        (("P23G-ad", "TEggRE"), "their"),
        (("P23Gpn<pr", "HIREN"), "their"),
        (("P23GpnplOd{rh}", "HVRES"), "their"),
        (("P23Gpnpn{rh}", "yAIRIS"), "their"),
        (("P23N", "YAI"), "they"),
        (("P23N-ad{rh}", "TAI"), "they"),
        (("P23N>=", "HEO"), "they"),
        (("P23N>={rh}", "yAI"), "they"),
        (("P23NX", "HEMSELUEN"), "themself"),
        (("P23<prX", "YAm"), "them"),
        (("P23<prX", "HEOmSaeLF"), "themself"),
        (("P23MX", "HAM"), "them"),
        (("P23OdX-as", "TAIM"), "them"),
        (("P23X", "HEMSOLUE"), "themself"),
        (("P23<pr", "zAM"), "them"),
        (("P23<pr>=", "HAm"), "them"),
        (("P23Od-ad", "TAIM"), "them"),
        (("P23Od>={rh}", "HEM"), "them"),
        (("P23Oi", "HEON"), "them"),
        (("P23Oi-as", "TAIm"), "them"),
        (("P23Oi{rh}", "HEOM"), "them"),
        (("P23Oi", "yEggM"), "them"),
        (("P23Od", "zAm"), "them"),
        (("P23>pr", "EM"), "them"),
    ]
)
def test_pronoun_parsing(instance: tuple[str, str], want: str) -> None:
    p = prons.Pronoun(*instance)
    have = p.mapped
    assert have == want
