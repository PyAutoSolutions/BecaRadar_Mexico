from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/config.py
# parents[3] = raíz de BecaRadar_Mexico
PROJECT_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = PROJECT_ROOT / ".env.development"


class Settings(BaseSettings):
    PROJECT_NAME: str = "BecaRadar México API"
    API_V1_PREFIX: str = "/api/v1"

    # Base de datos
    DATABASE_URL: str

    # Seguridad
    SECRET_API_KEY: str
    BACKEND_API_KEY: str

    # Backend
    BACKEND_API_URL: str = "http://localhost:8000/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]

    # Entorno
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Telegram
    TELEGRAM_BOT_TOKEN: str

    # Rate limit
    RATE_LIMIT_MENSAJES: int = 5
    RATE_LIMIT_VENTANA_SEGUNDOS: int = 10

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()