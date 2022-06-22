"""Write controls the output of manx parse command."""

# Standard library imports
from __future__ import annotations
import csv
import enum
import json
from typing import Text, TextIO, TypedDict

# Third-party library imports
from tqdm import tqdm

# Local library imports
from manx import nlp


__all__ = ["Format", "write"]


T5_PREFIX = "Lemmatize"

DEFAULT_NGRAM_SIZE = 11


class WriteError(Exception):
    ...


class WriteFormatError(WriteError):
    ...


class Format(str, enum.Enum):
    FullText = "full"
    StripText = "strip"
    JSONLines = "jsonlines"
    T5input = "t5"


class T5line(TypedDict):
    prefix: str
    input_text: str
    target_text: str


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
) -> list[T5line]:
    if verbose:
        itr = tqdm(docs, desc="Writing documents")
    else:
        itr = docs

    result: list[T5line] = []

    t5_prefix = T5_PREFIX

    for doc in itr:
        ngrams = nlp.ngrams(doc, n=ngram_size)

        for ngram in ngrams:
            input_text = " ".join(tkn.stripped_form for tkn in ngram)
            target_text = " ".join(tkn.stripped_lexel for tkn in ngram)
            result.append(
                {
                    "prefix": t5_prefix,
                    "input_text": input_text,
                    "target_text": target_text,
                }
            )
    return result


def write(
    fp: TextIO,
    docs: list[nlp.Doc],
    fmt: Format = Format.StripText,
    verbose: bool = True,
    ngram_size: int = DEFAULT_NGRAM_SIZE,
) -> None:
    """Write out corpus contents to target file in a given format."""
    match fmt:
        case Format.FullText | Format.StripText | Format.JSONLines:
            output_str = marshall_string(docs, fmt, verbose)
            fp.write(output_str)
        case Format.T5input:
            output_csv = marshall_csv(docs, verbose, ngram_size)
            fields = ["prefix", "input_text", "target_text"]
            writer = csv.DictWriter(
                fp,
                fieldnames=fields,
                quoting=csv.QUOTE_ALL,
                escapechar="\\",
            )
            writer.writeheader()
            writer.writerows(output_csv)
        case _:
            raise WriteFormatError(f"{fmt.value} formatting is not supported")
