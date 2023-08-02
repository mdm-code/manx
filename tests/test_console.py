"""Tests of the CLI interface."""

# Standard library imports
import argparse
from contextlib import nullcontext as does_not_raise
from dataclasses import dataclass
from io import BytesIO, StringIO

# Third-party imports
import pytest

# Local library imports
from manx import console, nlp, writing
from manx.model import settings
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


def test_console_download(mocker) -> None:
    """Test if the download subcommand can be invoked from the CLI."""
    opn = mocker.mock_open()
    mkdir = mocker.Mock()
    mocker.patch("builtins.open", opn)
    mocker.patch("os.mkdir", mkdir)

    @dataclass
    class MockResponse:
        text: BytesIO = BytesIO(bytes("", encoding="utf8"))

        def read(self) -> BytesIO:
            self.text.decode = lambda _: self.text  # type: ignore
            return self.text

        def raise_for_status(self) -> None:
            return None

        @property
        def status_code(self) -> int:
            return 200

    mocker.patch("httpx.AsyncClient.get", return_value=MockResponse())

    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            command="download",
            root="dump",
            verbose=False,
        ),
    )

    with does_not_raise():
        console.main()


def test_console_parse(docs: list[nlp.Doc], mocker) -> None:
    """See if the parse subcommand can be invoked from the CLI."""
    mocker.patch("manx.console.load", return_value=docs)
    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            command="parse",
            from_web=False,
            verbose=False,
            root="",
            output=StringIO(""),
            format=writing.Format.T5input,
            ngram_size=settings.DEFAULT_NGRAM_SIZE,
            chunk_size=settings.DEFAULT_CHUNK_SIZE,
            prefix=settings.T5_PREFIX,
        )
    )
    with does_not_raise():
        console.main()


def test_console_api(mocker) -> None:
    """Check if the api subcommand can be invoked from the CLI."""
    mocker.patch("manx.console.api.run", return_value=None)
    mocker.patch(
        "argparse.ArgumentParser.parse_args",
        return_value=argparse.Namespace(
            command="api",
            host=settings.API_HOST,
            port=settings.API_PORT
        )
    )
    with does_not_raise():
        console.main()
