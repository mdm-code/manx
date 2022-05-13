"""Tests for the download module."""

# Standard library imports
from dataclasses import dataclass
from io import BytesIO
from unittest import mock

# Third-party library imports
import pytest

# Local library imports
from manx.corpus import download
from manx.corpus import file
from manx.corpus import fs


@pytest.fixture
def web_contents() -> str:
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">

<html>
<head>
<title>Index of /ihd/laeme2/tagged_data</title>
</head>
<body>
<h1>Index of /ihd/laeme2/tagged_data</h1>
<table>
<tr><th valign="top"><img alt="[ICO]" src="/icons/blank.gif"/></th><th><a
href="?C=N;O=D">Name</a></th><th><a href="?C=M;O=A">Last
modified</a></th><th><a href="?C=S;O=A">Size</a></th><th><a
href="?C=D;O=A">Description</a></th></tr> <tr><th colspan="5"><hr/></th></tr>
<tr><td valign="top"><img alt="[PARENTDIR]" src="/icons/back.gif"/></td><td><a
href="/ihd/laeme2/">Parent Directory</a></td><td> </td><td align="right">  -
</td><td> </td></tr> <tr><td valign="top"><img alt="[TXT]"
src="/icons/text.gif"/></td><td><a
href="aberdeent.html">aberdeent.html</a></td><td align="right">2017-10-26 14:48
</td><td align="right">2.8K</td><td> </td></tr> <tr><td valign="top"><img
alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="aberdeent.tag">aberdeent.tag</a></td><td align="right">2019-05-14 15:31
</td><td align="right">3.1K</td><td> </td></tr> <tr><td valign="top"><img
alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthcreedt.txt">worcthcreedt.txt</a></td><td align="right">2016-09-22
17:55  </td><td align="right">3.0K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthcreedt_mysql.txt">worcthcreedt_mysql.txt</a></td><td
align="right">2019-05-14 15:33  </td><td align="right">5.9K</td><td> </td></tr>
<tr><td valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthfragst.html">worcthfragst.html</a></td><td align="right">2017-06-27
11:32  </td><td align="right"> 46K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthfragst.tag">worcthfragst.tag</a></td><td align="right">2019-05-14
15:32  </td><td align="right"> 67K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthfragst.txt">worcthfragst.txt</a></td><td align="right">2016-09-22
17:55  </td><td align="right"> 27K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthfragst_mysql.txt">worcthfragst_mysql.txt</a></td><td
align="right">2019-05-14 15:33  </td><td align="right"> 48K</td><td> </td></tr>
<tr><td valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthgrglt.html">worcthgrglt.html</a></td><td align="right">2020-11-16
13:29  </td><td align="right">482K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthgrglt.tag">worcthgrglt.tag</a></td><td align="right">2020-11-16
13:28  </td><td align="right">464K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthgrglt.txt">worcthgrglt.txt</a></td><td align="right">2016-09-22
17:55  </td><td align="right">191K</td><td> </td></tr> <tr><td
valign="top"><img alt="[TXT]" src="/icons/text.gif"/></td><td><a
href="worcthgrglt_mysql.txt">worcthgrglt_mysql.txt</a></td><td
align="right">2019-05-14 15:33  </td><td align="right">213K</td><td> </td></tr>
<tr><th colspan="5"><hr/></th></tr>
</table>
</body></html>
"""


@pytest.fixture
def parents() -> fs.Dir:
    root = fs.Dir("root", files=[])
    return root / fs.Dir("dicts", [])


@pytest.mark.parametrize(
    "text, expected",
    [
        ("arundel248t.tag", True),
        ("ashmole360t.txt", True),
        ("bestiaryt_mysql.txt", True),
        ("worcthfragst.html", False),
        ("?C=M;O=A", False),
    ],
)
def test_filter_elaeme(text: str, expected: bool) -> None:
    f = download.LAEMEFileFilter()
    have = f(text)
    assert have == expected


def test_link_parser(web_contents) -> None:
    parser = download.LinkParser(filters=[download.LAEMEFileFilter()])
    have = parser.parse(web_contents)
    assert len(have) == 9


@pytest.mark.parametrize(
    "filters, text, expected",
    [
        ([download.LAEMEFileFilter()], "worcthcreedt.txt", True),
        ([download.LAEMEFileFilter()], "worcthfragst.tag", True),
        ([download.LAEMEFileFilter()], "worcthcreedt_mysql.txt", True),
        ([download.LAEMEIgnoredFiles()], "filelist.txt", False),
        ([download.LAEMEIgnoredFiles()], "filelist_base.txt", False),
        ([download.LAEMEIgnoredFiles()], "digbysiritht.txt", False),
        ([download.LAEMEIgnoredFiles()], "worcthfragst.tag", True),
        ([], "worcthgrglt.html", True),
        (None, "worcthgrglt.dic", True),
    ],
)
def test_bs_apply(filters, text, expected) -> None:
    parser = download.LinkParser(filters=filters)
    have = parser._apply(text)
    assert have == expected


@pytest.mark.parametrize(
    "base, url, expected",
    [
        (
            "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/",
            "dulwicht.txt",
            "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/dulwicht.txt",
        ),
        (
            "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/",
            "digpmt_mysql.txt",
            "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/digpmt_mysql.txt",
        ),
        (
            "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/",
            "?C=S;O=A",
            "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/?C=S;O=A",
        ),
    ],
)
def test_link_resolve(base: str, url: str, expected: str) -> None:
    have = download.Link(base, url).resolved
    assert have == expected


@pytest.mark.parametrize(
    "case",
    [
        download.Link(""),
        download.Link(),
    ],
)
def test_blank_link(case: download.Link) -> None:
    """Blank link evaluates to an empty string."""
    assert str(case) == ""


@pytest.mark.parametrize(
    "case, want",
    [
        (download.WebContents("", 200), True),
        (download.WebContents("", 203), False),
        (download.WebContents("", 403), False),
        (download.WebContents("", 404), False),
    ],
)
def test_web_contents_status(case: download.WebContents, want: bool) -> None:
    have = case.ok
    assert have == want


@pytest.mark.parametrize(
    "case, want",
    [
        (
            file.CorpusFile("eul107t.txt", download.WebContents("", 200)),
            file.FileType.Text,
        ),
        (
            file.CorpusFile(
                "add27909t_mysql.txt", download.WebContents("", 200)
            ),
            file.FileType.Dict,
        ),
        (
            file.CorpusFile(
                "royalkgct.html", download.WebContents("", 200)
            ),
            file.FileType.Html,
        ),
        (
            file.CorpusFile(
                "bodley57t.tag", download.WebContents("", 200)
            ),
            file.FileType.Tags,
        ),
        (
            file.CorpusFile("", download.WebContents("", 200)),
            file.FileType.Unidentified,
        ),
        (
            file.CorpusFile("fonts.css", download.WebContents("", 200)),
            file.FileType.Unidentified,
        ),
    ],
)
def test_corpus_file_type(
    case: file.CorpusFile, want: file.FileType
) -> None:
    assert case.type == want


def test_corpus_file_type_param():
    """Check the hasattr code section of the method on CorpusFile."""
    case = file.CorpusFile("egstellat.txt", download.WebContents("", 200))
    _ = case.type
    assert case.type == file.FileType.Text


@pytest.mark.parametrize(
    "instance, text",
    [
        (
            file.CorpusFile("", download.WebContents("foo", 403)),
            "foo",
        ),
        (
            file.CorpusFile("", download.WebContents("bar", 200)),
            "bar",
        ),
        (
            file.CorpusFile("", download.WebContents("baz", 300)),
            "baz",
        ),
    ],
)
def test_corpus_file_promoted_fields(
    instance: file.CorpusFile, text: str
) -> None:
    assert instance.text == text


def test_corpus_file_saving(mocker) -> None:
    m = mocker.mock_open()
    mocker.patch("builtins.open", m)
    f = file.CorpusFile("file.txt", download.WebContents("foo", 201))
    directory = fs.Dir("", [])
    f.save(directory)
    m.assert_called_once_with(f.name, "w")
    m().write.assert_called_once_with("foo")


@pytest.mark.parametrize(
    "case, want",
    [
        (fs.Dir("foo", files=[]), "root/dicts/foo"),
        (fs.Dir("bar", files=[]), "root/dicts/bar"),
        (fs.Dir("baz", files=[]), "root/dicts/baz"),
    ],
)
def test_dir_path_property(
    case: fs.Dir, want: str, parents: fs.Dir
) -> None:
    joined = parents.join(case)
    assert joined.path == want


@pytest.mark.parametrize(
    "case",
    [
        fs.Dir("spam", files=[]),
        fs.Dir("ham", files=[]),
        fs.Dir("food", files=[]),
    ],
)
def test_dir_truediv(case: fs.Dir, parents: fs.Dir) -> None:
    joined = parents / case
    assert joined == parents.join(case)


def test_dir_truediv_error(parents) -> None:
    with pytest.raises(TypeError):
        parents / "foo"


def test_dir_traverse(mocker) -> None:
    opn = mocker.mock_open()
    mkdir = mocker.Mock()
    mocker.patch("builtins.open", opn)
    mocker.patch("os.mkdir", mkdir)

    dirs = [
        fs.Dir("root", files=[]),
        fs.Dir(
            "dicts",
            files=[
                file.CorpusFile(
                    "foo.txt", download.WebContents("hello", 200)
                ),
                file.CorpusFile(
                    "bar.txt", download.WebContents("world", 200)
                ),
            ],
        ),
        fs.Dir("texts", files=[]),
    ]

    root, current = dirs[0], dirs[0]
    for d in dirs[1:]:
        current = current / d

    fs.traverse(root)
    assert opn.called
    assert mkdir.called


def test_downloader(mocker, web_contents: str) -> None:
    """Check the downloader with a mocked response from the httpx package."""

    @dataclass
    class MockResponse:
        text: BytesIO = BytesIO(bytes(web_contents, encoding="utf8"))

        def read(self) -> BytesIO:
            self.text.decode = lambda _: self.text  # type: ignore
            return self.text

        def raise_for_status(self) -> None:
            return None

        @property
        def status_code(self) -> int:
            return 200

    mocker.patch("httpx.AsyncClient.get", return_value=MockResponse())

    parser = download.LinkParser(
        root_url=download.LAEME_DATA_URL,
        filters=[download.LAEMEFileFilter()],
    )
    downloader = download.Downloader()
    _ = downloader.download()

    downloader = download.Downloader(parser=parser)
    _ = downloader.download()


@pytest.mark.parametrize(
    "instance, want",
    [
        ("texts", True),
        ("dicts", True),
        ("tags",  True),
        ("htmls", False),
    ]
)
def test_validate_dir_name(instance: str, want: bool) -> None:
    has = fs.DirName.is_valid(instance)
    assert has == want


def test_files_works_on_empty_dir() -> None:

    def _mock_func(*_) -> fs.Dir:
        d = fs.Dir("temp", files=[])
        d / fs.Dir("subdir1", files=[])
        d / fs.Dir("subdir2", files=[])
        return d

    func = fs.files(_mock_func)
    has = func("foo")
    assert len(has) == 0


def test_dir_obj_from_root() -> None:
    with (
        mock.patch("os.path.isdir") as misdir,
        mock.patch("os.listdir") as mlsdir,
        mock.patch("pathlib.Path.is_dir") as mpisdir,
        mock.patch("pathlib.Path.is_file") as mpisfile,
        mock.patch(
            "builtins.open", mock.mock_open(read_data=""), create=False
        ) as _,
    ):
        misdir.return_value = True
        mpisdir.return_value = True
        mpisfile.return_value = True
        mlsdir.return_value = ["texts", "dicts"]

        _ = fs.from_root("root")
