"""Endpoint puts together a REST API for lemmatization."""

# Local library imports
from typing import Any

# Third-party library imports
from fastapi import FastAPI
from starlette.types import ASGIApp
import uvicorn

# Local library imports
from manx.config import settings
from manx.api.lemmatize import v1


__all__ = ["run", "app"]


app = FastAPI(description="Lemmatization API endpoint")

app.include_router(
    v1,
    prefix="/v1",
    tags=["Lemmatize"],
)


def run(
    app: ASGIApp = app,
    host: str = settings.API_HOST,
    port: int = settings.API_PORT,
    **kwargs: Any,
) -> None:
    """Serve the lemmatization REST API."""
    uvicorn.run(app=app, host=host, port=port, **kwargs)


if __name__ == "__main__":
    run(app=app, host=settings.API_HOST, port=settings.API_PORT)
