# Third-party library imports
import pytest

# Local library imports
from manx.corpus.download import Downloader
from manx.corpus.file import CorpusFile
from manx.corpus.fs import FileContents
from manx.loading import load


@pytest.fixture
def files() -> list[CorpusFile]:
    tag_files = [
        CorpusFile(
            name=f"file_{i}.tag",
            contents=FileContents(text="$ge:ara/av_YORE\n$be/vpt13_WAS"),
        ) for i in range(10)
    ]
    return tag_files


@pytest.mark.parametrize(
    "verbose",
    [
        False,  # Avoid tqdm error
    ]
)
@pytest.mark.parametrize(
    "from_web",
    [
        True,
        False,
    ]
)
def test_load(
    verbose: bool,
    from_web: bool,
    files: list[CorpusFile],
    monkeypatch,
) -> None:
    """Verify is corpus files are loaded into a list."""
    monkeypatch.setattr(Downloader, "download", lambda x, y: files)
    monkeypatch.setattr("manx.corpus.fs.from_root", lambda: files)
    root = "/"
    load(from_web=from_web, root=root, verbose=verbose)


def test_load_error() -> None:
    """Chekc if empty root string raises value error."""
    with pytest.raises(ValueError):
        load(from_web=False, verbose=False, root="")
