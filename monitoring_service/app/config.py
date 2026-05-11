import os
from pathlib import Path

from pydantic_settings import BaseSettings

APP_ENV = os.getenv("APP_ENV", "development")

_ENV_FILES: dict[str, str] = {
    "development": ".env.development",
    "testing": ".env.testing",
    "production": ".env.production",
}


def _resolve_env_file() -> str | None:
    filename = _ENV_FILES.get(APP_ENV, ".env.development")
    path = Path(filename)
    return str(path) if path.exists() else None


class Settings(BaseSettings):
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+asyncpg://monitor_user:monitor_pass@localhost:5434/monitoring_db"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    OTEL_ENDPOINT: str | None = None

    LOG_LEVEL: str = "INFO"
    DEBUG: bool = False
    CORS_ORIGINS: str = "*"

    model_config = {
        "env_file": _resolve_env_file(),
        "extra": "ignore",
    }


settings = Settings()
