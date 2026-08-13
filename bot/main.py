import logging

from bot.core.bot import build_application
from bot.core.config import get_bot_config

# Configuración básica de logging para consola
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    config = get_bot_config()
    
    # Ajustar nivel de log según configuración
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger.setLevel(config.LOG_LEVEL)
    
    logger.info("Iniciando BecaRadar Bot...")
    
    application = build_application(config)
    
    # Inicia el polling continuo
    logger.info("Polling a Telegram iniciado.")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()