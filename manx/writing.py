"""Write controls the output of manx parse command."""

# Standard library imports
from __future__ import annotations
import csv
import enum
import json
from typing import Generator, Text, TextIO, TypedDict

# Third-party library imports
from tqdm import tqdm

# Local library imports
from manx import nlp


__all__ = ["Format", "write"]


T5_PREFIX = "Lemmatize"
DEFAULT_NGRAM_SIZE = 11
DEFAULT_CHUNK_SIZE = 200


class WriteError(Exception):
    ...


class WriteFormatError(WriteError):
    ...


class OutputError(WriteError):
    ...


class Format(str, enum.Enum):
    FullText = "full"
    StripText = "strip"
    JSONLines = "jsonlines"
    T5input = "t5"


class T5line(TypedDict):
    id: int
    prefix: str
    input: str
    target: str


def marshall_string(
    docs: list[nlp.Doc], fmt: Format, verbose: bool = False
) -> Text:
    if verbose:
        itr = tqdm(docs, desc="Writing documents")
    else:
        itr = docs

    match fmt:
        case Format.FullText:
            return "\n".join(d.text(strip=False) for d in itr)
        case Format.StripText:
            return "\n".join(d.text(strip=True) for d in itr)
        case Format.JSONLines:
            return "\n".join(json.dumps(d.asdict()) for d in itr)
        case _:
            raise WriteFormatError(
                f"{fmt.value} formatting is not supported by this function"
            )


def marshall_csv(
    docs: list[nlp.Doc],
    verbose: bool = False,
    ngram_size: int = DEFAULT_NGRAM_SIZE,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    t5prefix: str = T5_PREFIX,
) -> list[T5line]:
    """marshall_csv splits LAEME docs into CSV input lines for T5 training.

    The function attribute `chunk_size` sets the size of a single chunk
    obtained from a LAEME document.

    This function first (1) splits individual LAEME documents into chunks and
    (2) shuffles the chunks.
    """
    result: list[T5line] = []

    chunks = [
        d[i : i + chunk_size]
        for d in docs
        for i in range(0, len(d), chunk_size)
    ]

    def counter(start: int = 0, step: int = 1) -> Generator[int, None, None]:
        while True:
            yield start
            start += step

    idx = counter()

    if verbose:
        chunks = tqdm(chunks, desc=f"Writing {len(chunks)} chunks")

    for chunk in chunks:
        ngrams = nlp.ngrams(chunk, n=ngram_size)

        for ngram in ngrams:
            input = " ".join(tkn.stripped_form for tkn in ngram)
            target = " ".join(tkn.stripped_lexel for tkn in ngram)
            result.append(
                {
                    "id": next(idx),
                    "prefix": t5prefix,
                    "input": input,
                    "target": target,
                }
            )

    return result


def write(
    docs: list[nlp.Doc],
    output: TextIO,
    fmt: Format = Format.StripText,
    verbose: bool = True,
    ngram_size: int = DEFAULT_NGRAM_SIZE,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    t5prefix: str = T5_PREFIX,
) -> None:
    """Write out corpus contents to target file in a given format.

    Specify `output` for a single output. Otherwise, for T5 output, provide
    file buffers as `train`, `valid`, `test` arguments.
    """
    match fmt:
        case Format.FullText | Format.StripText | Format.JSONLines:
            output_str = marshall_string(docs, fmt, verbose)
            output.write(output_str)
        case Format.T5input:
            result = marshall_csv(
                docs, verbose, ngram_size, chunk_size, t5prefix
            )
            fields = list(T5line.__annotations__.keys())
            writer = csv.DictWriter(
                output,
                fieldnames=fields,
                quoting=csv.QUOTE_ALL,
                escapechar="\\",
            )
            writer.writeheader()
            writer.writerows(result)
        case _:
            raise WriteFormatError(f"{fmt.value} formatting is not supported")
