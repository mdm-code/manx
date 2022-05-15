# Standard library imports
from __future__ import annotations
from contextlib import redirect_stderr
from dataclasses import asdict, dataclass
import multiprocessing
from os import PathLike
from typing import Literal


# Third-party library imports
import fasttext
import numpy as np


__all__ = ["load", "Model", "Parameters", "train"]


@dataclass(slots=True, frozen=True)
class Parameters:
    input: str
    model: Literal["skipgram", "cbow"] = "skipgram"
    lr: float = 0.05
    dim: int = 100
    ws: int = 5
    epoch: int = 5
    minCount: int = 5
    minn: int = 3
    maxn: int = 6
    neg: int = 5
    wordNgrams: int = 1
    loss: Literal["ns", "hs", "softmax", "ova"] = "ns"
    bucket: int = 2_000_000
    thread: int = multiprocessing.cpu_count() - 1
    lrUpdateRate: int = 100
    t: float = 1e-4
    verbose: int = 2


class Model:
    _instance: Model | None = None

    def __init__(self, trained: fasttext.FastText._FastText) -> None:
        self._trained = trained

    # NOTE: *args, **kwargs are passed to __init__
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def save(self, fpath: PathLike[str]) -> None:
        self._trained.save_model(fpath)

    def get_word_vector(self, word: str) -> np.ndarray:
        return self._trained.get_word_vector(word)


def load(fpath: PathLike[str]) -> Model:
    """Load FastText model given a file path."""
    # NOTE: Monkey patch eprint on FastText to silence the warning message
    fasttext.FastText.eprint = lambda _: None
    try:
        loaded = fasttext.load_model(fpath)
    except ValueError:
        raise ValueError(f"{fpath} cannot be loaded!")
    return Model(trained=loaded)


def train(params: Parameters) -> Model:
    """Train FastText model with specified parameters.

    Refer to https://fasttext.cc/docs/en/unsupervised-tutorial.html to
    experiment with training optional parameters.
    """
    trained = fasttext.train_unsupervised(**asdict(params))
    return Model(trained=trained)
