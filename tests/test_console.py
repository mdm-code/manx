"""Tests of the CLI interface."""

# Standard library imports
import argparse
from contextlib import nullcontext as does_not_raise
from dataclasses import dataclass
from io import BytesIO

# Third-party library imports
import pytest

# Local library imports
from manx import console


def test_console_download(mocker) -> None:
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
