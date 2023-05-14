# Third party library imports
from fastapi import FastAPI, APIRouter
from pydantic import BaseSettings, BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import uvicorn


def ngrams(tokens: list[str], n: int = 11) -> list[str]:
    return [" ".join(x) for x in zip(*[tokens[n:] for n in range(n)])]


class ModelService:
    """"""

    def __init__(
        self, name: str, prefix: str = "lemmatize", n_tokens: int = 11
    ) -> None:
        self.prefix = prefix
        self.n_tokens = n_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(name)

    def decode(self, input: str) -> str:
        result = []
        tokens = input.split()
        target_token = self.n_tokens // 2

        for i in range(target_token):
            input_ids = self.tokenizer(
                self.prefix + ": ".join(tokens[i : self.n_tokens + i]),
                return_tensors="pt",
            ).input_ids
            outputs = self.model.generate(input_ids, num_beams=5)
            decoded = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True
            )
            result.append(decoded.split()[0])

        for ngram in ngrams(input.split(), self.n_tokens):
            input_ids = self.tokenizer(
                self.prefix + ": " + ngram, return_tensors="pt"
            ).input_ids
            outputs = self.model.generate(input_ids, num_beams=5)
            decoded = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True
            )
            result.append(decoded.split()[target_token])

        to_rev = []

        for i in range(1, target_token + 1):
            input_ids = self.tokenizer(
                self.prefix + ": ".join(tokens[len(tokens) - self.n_tokens :]),
                return_tensors="pt",
            ).input_ids
            outputs = self.model.generate(input_ids, num_beams=5)
            decoded = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True
            )
            to_rev.append(decoded.split()[-i])

        result.extend(reversed(to_rev))

        return " ".join(result)


class Settings(BaseSettings):
    class Config:
        env_prefix = "MANX_"

    MODEL_PATH: str = "melt5"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000


settings = Settings()

app = FastAPI()

v1 = APIRouter()


class Input(BaseModel):
    decoded: str


model_service = ModelService(settings.MODEL_PATH)


@v1.post("/healthcheck")
def healthcheck(
    input: Input,
) -> Input:
    return Input(decoded=model_service.decode(input.decoded))


app.include_router(v1, prefix="/api/v1")


def run(*, host: str, port: int) -> None:
    """Run the manx T5 lemmatization API."""
    uvicorn.run(app, host=host, port=port)
