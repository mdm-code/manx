"""Tests for the download module."""

# Third-party library imports
import pytest

# Local library imports
from manx import download


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


@pytest.mark.parametrize(
    "text, expected",
    [
        ("arundel248t.tag", False),
        ("ashmole360t.txt", True),
        ("bestiaryt_mysql.txt", True),
        ("worcthfragst.html", False),
        ("?C=M;O=A", False),
    ]
)
def test_filter_elaeme(text: str, expected: bool) -> None:
    f = download.ELALMEFileFilter()
    result = f(text)
    assert result == expected


def test_bs_parser(web_contents) -> None:
    parser = download.BSParser(filters=[download.ELALMEFileFilter()])
    result = parser.parse(web_contents)
    assert len(result) == 6


@pytest.mark.parametrize(
    "filters, text, expected",
    [
        ([download.ELALMEFileFilter()], "worcthcreedt.txt", True),
        ([download.ELALMEFileFilter()], "worcthfragst.tag", False),
        ([download.ELALMEFileFilter()], "worcthcreedt_mysql.txt", True),
        ([], "worcthgrglt.html", True),
        (None, "worcthgrglt.dic", True),
    ]
)
def test_bs_apply(filters, text, expected) -> None:
    parser = download.BSParser(filters=filters)
    result = parser._apply(text)
    assert result == expected


def test_downloader() -> None:
    parser = download.BSParser([download.ELALMEFileFilter()])
    downloader = download.Downloader(parser=parser)
    downloader.download()
