"""Loading provides an interface for loading in corpus data."""

# Standard library imports
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from os import PathLike
import sys

# Third-party library imports
from tqdm import tqdm

# Local library imports
from manx import corpus, embedding, nlp, parsing


__all__ = ["load"]


def load(
    *,
    model_path: PathLike[str] | None,
    from_web: bool = False,
    root: str = "",
    verbose: bool = False,
) -> list[nlp.Doc]:
    """Load LAEME corpus data."""
    if model_path is None:
        model = None
    else:
        try:
            model = embedding.load(model_path)
        except ValueError:
            print(
                f"failed to load {model_path} FastText model! "
                "Word embeddings will not be computed.",
                file=sys.stderr,
            )
            model = None

    if from_web:
        downloader = corpus.Downloader()
        files = downloader.download(verbose)
    else:
        if not root or not Path(root).exists():
            raise ValueError(f"{root} does not exist!")
        files = corpus.from_root(root)
    source_files = [
        (f.stem, f.as_io()) for f in files if f.type == corpus.FileType.Tags
    ]

    parser: parsing.TagParser = parsing.TagParser()

    if verbose:
        result = [
            nlp.doc(list(parser.parse(file)), model=model, label=label)
            for label, file in tqdm(source_files, desc="parsing tag files")
        ]
    else:
        result = [
            nlp.doc(list(parser.parse(file)), model=model, label=label)
            for label, file in source_files
        ]
    return result
