from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Metamong"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""

    # Security
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    SECRET_KEY: str = ""

    # DB
    DATABASE_URL: str = ""
    DB_PASSWORD: str = ""

    BACKEND_URL: str = ""

    model_config = SettingsConfigDict(
        env_file=".env"
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
