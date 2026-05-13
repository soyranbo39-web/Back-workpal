from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    AUTH_SECRET_KEY: SecretStr = Field(..., min_length=32)
    AUTH_ALGORITHM: str
    AUTH_TOKEN_EXPIRE_MINUTES: int
    AUTH_COOKIE_NAME: str
    AUTH_COOKIE_SECURE: bool
    AUTH_COOKIE_HTTPONLY: bool
    AUTH_COOKIE_SAMESITE: str
    SQLITE_DB_PATH: str
    API_KEY_HEADER_NAME: str
    API_KEY_VALUE: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

settings = Settings()

# Export constants expected by the rest of the app modules.
AUTH_SECRET_KEY = settings.AUTH_SECRET_KEY.get_secret_value()
AUTH_JWT_ALGORITHM = settings.AUTH_ALGORITHM
AUTH_TOKEN_EXPIRE_MINUTES = settings.AUTH_TOKEN_EXPIRE_MINUTES
AUTH_COOKIE_NAME = settings.AUTH_COOKIE_NAME
AUTH_COOKIE_SECURE = settings.AUTH_COOKIE_SECURE
AUTH_COOKIE_HTTPONLY = settings.AUTH_COOKIE_HTTPONLY
AUTH_COOKIE_SAMESITE = settings.AUTH_COOKIE_SAMESITE
API_KEY_HEADER_NAME = settings.API_KEY_HEADER_NAME
API_KEY_VALUE = settings.API_KEY_VALUE

SQLITE_DB_PATH = Path(settings.SQLITE_DB_PATH)
DATABASE_URL = f"sqlite:///{SQLITE_DB_PATH}"