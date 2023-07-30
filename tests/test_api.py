# Standard library imports
from unittest import mock

# Third-party library imports
import fastapi
from fastapi.testclient import TestClient
import pytest

# Local library imports
from manx.api import app
from manx.api.data_model import Response
from manx.api.lemmatize import _process
from manx.config import settings


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


class TestAPI:

    def test_health(self, client: TestClient) -> None:
        """Check if the health endpoint returns 200 when working correctly."""
        response = client.get("v1/health")
        assert response.status_code == fastapi.status.HTTP_200_OK

    def test_lemmatize(self, client: TestClient) -> None:
        """Test if the lemmatization endpoint works as expected."""
        def _func(*args, **kwargs) -> str:
            return settings.API_TEXT_PLACEHOLDER

        with mock.patch("manx.api.lemmatize._process", new=_func):
            response = client.post(
                url="v1/lemmatize",
                json={
                    "text": settings.API_TEXT_PLACEHOLDER,
                    "window_size": settings.DEFAULT_NGRAM_SIZE
                }
            )
        assert response.status_code == fastapi.status.HTTP_200_OK
        assert response.json() == dict(
            Response(text=settings.API_TEXT_PLACEHOLDER)
        )


@pytest.mark.parametrize(
    "text",
    [
        " ".join(settings.API_TEXT_PLACEHOLDER.split()[:5]),
        " ".join(settings.API_TEXT_PLACEHOLDER.split()[:11]),
        settings.API_TEXT_PLACEHOLDER,
    ]
)
def test_process(text: str) -> None:
    """Test if the _process worker function operates as expected."""

    def _predict(text: str, _: str = settings.T5_PREFIX) -> list[str]:
        return [text]

    have = _process(
        text=text,
        window_size=settings.DEFAULT_NGRAM_SIZE,
        predict=_predict,
    )
    assert have == " ".join(text.split())
