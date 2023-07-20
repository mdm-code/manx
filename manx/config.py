from pydantic_settings import BaseSettings, SettingsConfigDict


PKG_NAME = "MANX_"

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


settings = Settings()
