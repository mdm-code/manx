"""Loading provides an interface for loading in corpus data."""

# Standard library imports
from __future__ import annotations
from pathlib import Path

# Third-party library imports
from tqdm import tqdm

# Local library imports
from manx import corpus, nlp, parsing


__all__ = ["load"]


def load(
    *,
    from_web: bool = False,
    root: str = "",
    verbose: bool = False,
) -> list[nlp.Doc]:
    """Load LAEME corpus data."""
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
            nlp.doc(list(parser.parse(file)), label=label)
            for label, file in tqdm(source_files, desc="Parsing tag files")
        ]
    else:
        result = [
            nlp.doc(list(parser.parse(file)), label=label)
            for label, file in source_files
        ]
    return result
