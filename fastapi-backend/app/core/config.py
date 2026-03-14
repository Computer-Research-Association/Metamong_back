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

    # URL
    BACKEND_URL: str = ""
    FRONTEND_URL: str = "" # Unity WEBGL 빌드가 호스팅 될 도메인

    # Environment
    NODE_ENV: str = "production"

    model_config = SettingsConfigDict(
        env_file=["../.env", ".env"]  # 루트 .env 우선, fastapi-backend/.env로 로컬 오버라이드 가능
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
