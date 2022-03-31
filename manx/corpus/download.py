"""Download interacts wiht the ELAEME website to download file contents."""

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod, abstractproperty
import asyncio
import enum
import httpx
import io
import os
from tqdm import tqdm
from typing import TYPE_CHECKING
import urllib.parse

# Third-party library imports
from bs4 import BeautifulSoup  # type: ignore

# Local library imports
if TYPE_CHECKING:
    from .file import Dir


__all__ = [
    "Downloader",
    "DownloadError",
    "ELALMEFileFilter",
    "FileType",
    "LinkParser",
]


ELAEME_DATA_URL = "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/"

ELALME_FILE_EXTS = [".txt"]

IGNORED_ELALME_FILES = [
    # NOTE: these two files contain file names only
    "filelist.txt",
    "filelist_base.txt",
    # NOTE: this is an empty text file; there is no mysql file for it
    "digbysiritht.txt",
    # NOTE: this file is forbidden
    "all_laeme_data.txt",
]


class DownloadError(Exception):
    ...


class Parser(ABC):
    def __init__(self, filters: list[Filter] | None = None) -> None:
        if not filters:
            self.filters: list[Filter] = []
        else:
            self.filters = filters

    @abstractmethod
    def parse(self, contents: str) -> list[Link]:
        raise NotImplementedError


class LinkParser(Parser):
    """LinkParser uses Beautiful Soup to retrieve file names aka links."""

    def __init__(
        self, root_url: str = "", filters: list[Filter] | None = None
    ) -> None:
        self.root_url = root_url
        super().__init__(filters)

    def parse(self, web_contents: str) -> list[Link]:
        return self._parse_links(web_contents)

    def _parse_links(self, web_contents: str) -> list[Link]:
        soup = BeautifulSoup(web_contents, "html.parser")
        ahrefs = soup.find_all("a")
        urls = list(filter(self._apply, map(lambda x: x.get("href"), ahrefs)))
        links = [Link(self.root_url, u) for u in urls]
        return links

    def _apply(self, link: str) -> bool:
        if not self.filters:
            return True
        for f in self.filters:
            if not f(link):
                return False
        return True


class Filter(ABC):
    def __init__(self, patterns: list[str]) -> None:
        self.patterns = patterns

    def __call__(self, text: str) -> bool:
        return self._filter(text)

    @abstractmethod
    def _filter(self, text: str) -> bool:
        pass


class ELALMEFileFilter(Filter):
    """ELALMEFileFilter filters out file names with the provided patterns."""

    def __init__(self, patterns: list[str] = ELALME_FILE_EXTS.copy()) -> None:
        super().__init__(patterns)

    def _filter(self, text: str) -> bool:
        return any(map(lambda x: text.endswith(x), self.patterns))


class ELAEMEIgnoredFiles(Filter):
    """ELAEMEIgnoredFiles filters out files that do not contribute to the corpus."""

    def __init__(
        self, patterns: list[str] = IGNORED_ELALME_FILES.copy()
    ) -> None:
        super().__init__(patterns)

    def _filter(self, text: str) -> bool:
        return not any(map(lambda x: text == x, self.patterns))


class Downloader:
    """Downloader handles downloading corpus files."""

    def __init__(
        self,
        root_url: str = ELAEME_DATA_URL,
        parser: Parser | None = None,
    ) -> None:
        self.root_url = root_url
        if not parser:
            self.parser: Parser = LinkParser(
                root_url=root_url,
                filters=[
                    ELALMEFileFilter(),
                    ELAEMEIgnoredFiles(),
                ],
            )
        else:
            self.parser = parser

    def download(self, verbose: bool = False) -> list[CorpusFile]:
        result = asyncio.run(self.adownload(verbose))
        return result

    async def adownload(self, verbose: bool = False) -> list[CorpusFile]:
        async with httpx.AsyncClient() as client:
            response = await self.read_website_contents(self.root_url, client)

            if not response.ok:
                raise DownloadError(
                    f"ERROR {response.status_code} on GET <{self.root_url}>"
                )

            all_links = self.parser.parse(response.text)

            result: list[CorpusFile] = []

            # NOTE: 5 is optimal on my OS given the number of file descriptors
            n = 5
            splits = [all_links[start::n] for start in range(n)]

            if verbose:
                bar = tqdm(total=len(all_links))
            else:
                bar = None

            for split in splits:
                tasks = []
                for link in split:
                    tasks.append(self.to_file(link, client, bar=bar))
                result.extend(await asyncio.gather(*tasks))
            return result

    async def to_file(
        self, link: Link, client: httpx.AsyncClient, **kwargs: tqdm | None
    ) -> CorpusFile:
        web_contents = await self.read_website_contents(str(link), client)
        if b := kwargs.get("bar", None):
            b.update(1)
        return CorpusFile(name=link.name, contents=web_contents)

    async def read_website_contents(
        self, url: str, client: httpx.AsyncClient
    ) -> WebContents:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            contents = response.read().decode("UTF-8")
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError:
                return WebContents("", response.status_code)
        return WebContents(contents, response.status_code)


class FileType(enum.Enum):
    Unidentified = 0
    Text = 1
    Dict = 2
    Html = 3
    Tags = 4


class Saver(ABC):
    @abstractmethod
    def save(self, node: Dir) -> None:
        pass


class CorpusFile(Saver):
    """CorpusFile represents a corpus text file from ELAEME."""

    def __init__(self, name: str, contents: Contents) -> None:
        self.name = name
        self.contents = contents

    @property
    def text(self) -> str:
        return self.contents.text

    def as_io(self) -> io.StringIO:
        return io.StringIO(self.contents.text)

    @property
    def type(self) -> FileType:
        if hasattr(self, "_type"):
            return self._type
        self._type: FileType = self._eval_type()
        return self._type

    def _eval_type(self) -> FileType:
        try:
            stem, *_, ext = self.name.split(".")
        except ValueError:
            stem, ext = "", ""
        match ext.lower():
            case "tag":
                return FileType.Tags
            case "html":
                return FileType.Html
            case "txt":
                if stem.split("_")[-1] == "mysql":
                    return FileType.Dict
                return FileType.Text
            case _:
                return FileType.Unidentified

    def save(self, node: Dir) -> None:
        with open(os.path.join(node.path, self.name), "w") as fout:
            fout.write(self.text)


class Contents(ABC):
    def __init__(self, text: str) -> None:
        self._text = text

    @abstractproperty
    def text(self) -> str:
        return self._text


class WebContents(Contents):
    def __init__(self, text: str, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(text=text)

    @property
    def text(self) -> str:
        return self._text

    @property
    def ok(self) -> bool:
        return self.status_code == 200


class FileContents(Contents):
    @property
    def text(self) -> str:
        return self._text


class Link:
    def __init__(self, *urls: str) -> None:
        if not urls:
            self.base = ""
            self.urls: tuple[str, ...] = tuple()
            self.name = ""
            return
        self.base = urls[0]
        self.urls = urls[1:]
        if self.urls:
            self.name = self.urls[-1]
        else:
            self.name = self.base

    def __str__(self) -> str:
        return self.resolved

    @property
    def resolved(self) -> str:
        prev = self.base
        for url in self.urls:
            prev = urllib.parse.urljoin(prev, url)
        return prev
