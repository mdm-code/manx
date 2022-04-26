"""Downloading provides a way to download LAEME corpus data as flat files."""

# Local library imports
from manx import corpus


__all__ = ["download"]


def download(root_dir: str, verbose: bool) -> None:
    """Download LAEME corpus data as flat files."""
    downloader = corpus.Downloader()
    files = downloader.download(verbose)
    root = corpus.Dir(root_dir, files=[])
    root / corpus.Dir(
        corpus.DirName.dicts.value,
        files=[f for f in files if f.type == corpus.FileType.Dict],
    )
    root / corpus.Dir(
        corpus.DirName.texts.value,
        files=[f for f in files if f.type == corpus.FileType.Text],
    )
    root / corpus.Dir(
        corpus.DirName.tags.value,
        files=[f for f in files if f.type == corpus.FileType.Tags],
    )
    corpus.traverse(root)
