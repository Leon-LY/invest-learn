"""Application configuration via pydantic-settings."""
import json
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "production"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production"
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = "postgresql+asyncpg://investlearn:investlearn123@localhost:5432/investlearn"
    DATABASE_URL_SYNC: str = "postgresql://investlearn:investlearn123@localhost:5432/investlearn"
    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── DeepSeek LLM (OpenAI-compatible API) ──
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ── Qwen Vision (通义千问 VL) ──
    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-vl-plus"  # or qwen-vl-max

    # ── Crawler network ──
    CRAWLER_HTTP_TIMEOUT: float = 30.0
    CRAWLER_RETRY_MAX: int = 3
    CRAWLER_RETRY_DELAY: float = 2.0
    HTTP_PROXY: str = ""
    HTTPS_PROXY: str = ""

    # ── AI analysis ──
    GENERATE_FAKE_CONTENT: bool = False  # no more template article content

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
