from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Metamong"

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Security
    JWT_SECRET: str
    SECRET_KEY: str

    # DB
    DATABASE_URL: str
    DB_PASSWORD: str
