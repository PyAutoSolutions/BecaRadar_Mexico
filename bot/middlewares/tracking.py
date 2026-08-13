import json
import logging
import os
from datetime import UTC, datetime

LOG_DIR = os.getenv("TRACKING_LOG_DIR", "./data")
os.makedirs(LOG_DIR, exist_ok=True)

TRACKING_FILE = os.path.join(
    LOG_DIR,
    "interacciones.jsonl",
)

logger_app = logging.getLogger(__name__)


def registrar_interaccion(
    telegram_user_id: int,
    comando: str,
) -> None:
    """
    Registra el evento de uso del bot sin bloquear la respuesta.
    """
    try:
        evento = {
            "telegram_user_id": telegram_user_id,
            "comando": comando,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        with open(
            TRACKING_FILE,
            "a",
            encoding="utf-8",
        ) as archivo:
            archivo.write(
                json.dumps(evento)
                + "\n"
            )

    except OSError as exc:
        logger_app.warning(
            "Error escribiendo tracking. "
            "El usuario no lo notará. Error: %s",
            exc,
        )
