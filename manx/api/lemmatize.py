"""Lemmatization router."""

# Standard library imports
import logging
from typing import Callable

# Third-party library imports
from fastapi import status, APIRouter

# Local library imports
from .data_model import Request, Response
from manx.model import t5


logging.basicConfig(format="%(levelname)s: %(message)s")

v1 = APIRouter()


@v1.post("/lemmatize")
async def process(request: Request) -> Response:
    """Lemmatize the provided early Middle English text."""
    result = _process(**dict(request))
    return Response(text=result)


@v1.get("/health")
async def health() -> int:
    """Check if the API endpoint is up and running."""
    return status.HTTP_200_OK


def _process(
    text: str,
    window_size: int = 11,
    predict: Callable[[str], list[str]] = t5.predict,
) -> str:
    """Pass the text to get lemmatization prediction from the model."""
    preds: list[str] = []
    words = [w for w in text.split() if w != ""]
    ngrams = list(
        zip(*[words[window_size:] for window_size in range(window_size)])
    )
    if len(ngrams) == 0:
        logging.warning(
            f"Text token length of {len(words)} is smaller than the size of "
            f"the context window of {window_size}. The model predition might "
            "be siginficantly worse."
        )
        result = predict(" ".join(words))[0]
        return result
    if len(ngrams) == 1:
        logging.warning(
            f"Text token length of {len(words)} is just about the size of "
            f"the context window of {window_size}. The model predition might "
            "be siginficantly worse."
        )
        result = predict(" ".join(ngrams[0]))[0]
        return result
    first, last, target = 0, len(ngrams) - 1, sum(divmod(window_size, 2))
    for i, ngram in enumerate(ngrams, start=first):
        pred = predict(" ".join(ngram))[0].split()
        if i == first:
            preds.extend(pred[: target + 1])
        elif i == last:
            preds.extend(pred[-target + 1 :])
        else:
            preds.append(pred[target])
    result = " ".join(preds)
    return result
