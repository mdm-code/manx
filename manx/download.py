"""The module is responsible for downloading manx input data from LAEME."""

# Standard library imports
from __future__ import annotations
from abc import ABC, abstractmethod
import urllib.request
from typing import TypeAlias

# Third-party library imports
from bs4 import BeautifulSoup  # type: ignore


Links: TypeAlias = list[str]


ELAEME_DATA_URL = "http://www.lel.ed.ac.uk/ihd/laeme2/tagged_data"

ELALME_FILE_EXTS = [".txt"]


class Parser(ABC):
    def __init__(self, filters: list[Filter] | None = None) -> None:
        if not filters:
            self.filters: list[Filter] = []
        else:
            self.filters = filters

    @abstractmethod
    def parse(self, web_contents: str) -> Links:
        raise NotImplementedError


class BSParser(Parser):
    def parse(self, web_contents: str) -> Links:
        soup = BeautifulSoup(web_contents, "html.parser")
        links = soup.find_all("a")
        links = list(filter(self._apply, map(lambda x: x.get("href"), links)))
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
            self.parser: Parser = BSParser()
        else:
            self.parser = parser

    # TODO: Things to do from this point on:
    #     ==== DOWNLOADING CD. ====
    #     1. The Downloader goes into the webpages and pulls their contents
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
    def download(self) -> None:
        response = urllib.request.urlopen(self.root_url)
        contents = response.read().decode("UTF-8")
        links = self.parser.parse(contents)
