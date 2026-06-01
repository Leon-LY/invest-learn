"""Application configuration via pydantic-settings."""
import json
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://investlearn:investlearn123@localhost:5432/investlearn"
    DATABASE_URL_SYNC: str = "postgresql://investlearn:investlearn123@localhost:5432/investlearn"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "CORS_ORIGINS":
                try:
                    return json.loads(raw_val)
                except (json.JSONDecodeError, TypeError):
                    return [o.strip() for o in raw_val.split(",")]
            return raw_val


settings = Settings()
