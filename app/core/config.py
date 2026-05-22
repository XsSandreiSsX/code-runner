from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI App (Default)"
    APP_VERSION: float = 1.0
    DEBUG: bool = True

    ALLOWED_ISSUERS: list = []

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
    )


settings = Settings()