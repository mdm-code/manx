# Standard library imports
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO

# Third-party library imports
import pytest

# Local library imports
from manx import nlp, writing
from manx.nlp.tokens import Token
from manx.parsing.tags import POS


@pytest.fixture
def docs() -> list[nlp.Doc]:
    tokens = [
        Token(
            lexel="",
            stripped_lexel="",
            grammel="",
            form="",
            stripped_form="",
            sequence=i,
            _pos=POS.Undef,
        ) for i in range(100)
    ]
    return [nlp.Doc(elems=tokens) for _ in range(10)]


@pytest.mark.parametrize(
    "fmt",
    [
        writing.Format.FullText,
        writing.Format.StripText,
        writing.Format.JSONLines,
    ]
)
@pytest.mark.parametrize(
    "verbose",
    [
        False,  # NOTE: True causes tqdm to fail
    ]
)
def test_marshall_string(
    docs: list[nlp.Doc],
    fmt: writing.Format,
    verbose: bool,
) -> None:
    """Test if all string formats are being marshalled."""
    with open("/dev/null") as f:
        with redirect_stderr(f), redirect_stdout(f):
            writing.marshall_string(docs=docs, fmt=fmt, verbose=verbose)



@pytest.mark.parametrize(
    "verbose",
    [
        False,  # NOTE: True causes tqdm to fail
    ]
)
def test_marshall_csv(docs: list[nlp.Doc], verbose: bool) -> None:
    """Test if invoked CSV marshalling function works as expected."""
    with open("/dev/null") as f:
        with redirect_stderr(f), redirect_stdout(f):
            writing.marshall_csv(docs=docs, verbose=verbose)


@pytest.mark.parametrize(
    "fmt",
    [
        writing.Format.FullText,
        writing.Format.StripText,
        writing.Format.JSONLines,
        writing.Format.T5input,
    ]
)
@pytest.mark.parametrize(
    "verbose",
    [
        False,  # NOTE: True causes tqdm to fail
    ]
)
def test_write(
    docs: list[nlp.Doc],
    fmt: writing.Format,
    verbose: bool,
) -> None:
    """Test the invokation of write with a string IO dump."""
    output = StringIO("")
    with open("/dev/null") as f:
        with redirect_stderr(f), redirect_stdout(f):
            writing.write(docs=docs, fmt=fmt, output=output, verbose=verbose)
