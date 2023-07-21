"""Config contains configurable parameters of the package."""

# Standard library imports
from typing import Literal

# Third-party library imports
from pydantic_settings import BaseSettings, SettingsConfigDict


PKG_NAME = "MANX"

TEXT_PLACEHOLDER = """
HON AN yESTER STUDE I STOD AN LUITEL STRIF TO HERE HOF AN BODI yAT
WAS OUNGOD yER HIT LAI ON yE BERE yO SPAK yE GOST MID DRERI MOD MID
REUyFOLE CHERE WO WORyE yI FLEIS yI FOULE BLOD WI LIGGEST yOU NOU
HERE IN HALLE yOU WERE FUL KENE yEWILE yOU WERE ONLIUE FALSE
DOMES TO DEME TO CHAUNGEN TWO TO FIUE yAT IS ME ONSENE NE WORyI
NEUEREMO BLIyE FUL SORE MAI I ME MENE
""".strip()


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_prefix=f"{PKG_NAME}_",
        env_file=".env",
        env_file_encoding="utf-8",
    )

    T5_PREFIX: str = "Lemmatize"
    DEFAULT_NGRAM_SIZE: int = 11
    DEFAULT_CHUNK_SIZE: int = 200

    API_HOST: str = "localhost"
    API_PORT: int = 8000
    API_LOG_LEVEL: str = "INFO"
    API_TEXT_PLACEHOLDER: str = TEXT_PLACEHOLDER

    MODEL_TYPE: Literal["byt5", "mt5", "t5"] = "byt5"
    MODEL_DIR: str = "mdm-code/me-lemmatize-byt5-small"
    USE_GPU: bool = False


settings = Settings()
