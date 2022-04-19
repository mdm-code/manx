from abc import ABC, abstractmethod
class Parser(ABC):
    @abstractmethod
    def parse(self, fp: TextIO) -> Generator[Any, None, None]:
        raise NotImplementedError
