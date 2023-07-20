"""REST API data transfer models."""

# Local library imports
from pydantic import BaseModel, Field

# Local library imports
from manx.config import settings


class Request(BaseModel):
    text: str = Field(
        default=settings.API_TEXT_PLACEHOLDER,
        description="Body of the text to lemmatize",
    )
    window_size: int = Field(
        default=settings.DEFAULT_NGRAM_SIZE,
        description=(
            "Size of the ngram window used for fine-tuning the ByT5 model"
        ),
    )


class Response(BaseModel):
    text: str = Field(default="", description="Body of the lemmatized text")
