"""The module is responsible for downloading manx input data from LAEME."""

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
import urllib.error
import urllib.parse
import urllib.request

# Third-party library imports
from bs4 import BeautifulSoup  # type: ignore


ELAEME_DATA_URL = "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data/"

ELALME_FILE_EXTS = [".txt"]


class Parser(ABC):
    def __init__(self, filters: list[Filter] | None = None) -> None:
        if not filters:
            self.filters: list[Filter] = []
        else:
            self.filters = filters

    @abstractmethod
    def parse(self, web_contents: str) -> list[Link]:
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
            if f(link):
                return True
        return False


class Filter(ABC):
    def __init__(self, patterns: list[str]) -> None:
        self.patterns = patterns

    def __call__(self, text: str) -> bool:
        return self._filter(text)

    @abstractmethod
    def _filter(self, text: str) -> bool:
        raise NotImplementedError


class ELALMEFileFilter(Filter):
    """ELALMEFileFilter filters out file names with the provided patterns."""

    def __init__(self, patterns: list[str] = ELALME_FILE_EXTS.copy()) -> None:
        super().__init__(patterns)

    def _filter(self, text: str) -> bool:
        return any(map(lambda x: text.endswith(x), self.patterns))


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
                root_url=root_url, filters=[ELALMEFileFilter()]
            )
        else:
            self.parser = parser

    # TODO: Things to do from this point on:
    #     ==== DOWNLOADING CD. ====
    #     2. Contents are then stored as File objects
    #
    #     ==== SAVING ====
    #     1. There are two types of files dict files (the ones with mysql)
    #        and text files with the actual contents of the corpus
    #     2. The two have to be kept separate; possibly with a subclass
    #        of Filter
    #     3. There has to be a FS class taking some root and then two
    #        subdirectories for `dicts` and `texts`
    #     4. It has to check whether the root exists, and inform the user
    #        that it does and stop the program execution
    #     5. Individual contents of the file are then to be written to the
    #        appropritate subdirectories
    def download(self) -> None:  # TODO: this guy should return some container
        contents = self.read_website_contents(self.root_url)
        links = self.parser.parse(contents)

        texts = []
        for l in links:
            try:
                text = self.read_website_contents(str(l))
            except urllib.error.HTTPError:
                # NOTE: catch HTTP Error 403: Forbidden for all_laeme_data.txt
                continue
            else:
                texts.append(text)

    def read_website_contents(self, url: str) -> str:
        response = urllib.request.urlopen(url)
        contents = response.read().decode("UTF-8")
        return contents


class Link:
    def __init__(self, *urls: str) -> None:
        if not urls:
            self.base = ""
            self.urls: tuple[str, ...] = tuple()
            return
        self.base = urls[0]
        self.urls = urls[1:]

    def __str__(self) -> str:
        return self.resolved

    @property
    def resolved(self) -> str:
        prev = self.base
        for url in self.urls:
            prev = urllib.parse.urljoin(prev, url)
        return prev
