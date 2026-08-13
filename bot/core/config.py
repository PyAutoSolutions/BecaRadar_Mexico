from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# bot/core/config.py
# La raíz del proyecto es tres niveles arriba de este archivo.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env.development"


class BotSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str

    BACKEND_API_URL: str = "http://localhost:8000/api/v1"
    BACKEND_API_KEY: str

    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_MENSAJES: int = 5
    RATE_LIMIT_VENTANA_SEGUNDOS: int = 10

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_bot_config() -> BotSettings:
    return BotSettings()