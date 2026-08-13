import logging

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from bot.core.config import BotSettings, get_bot_config
from bot.handlers import (
    alertas_handler,
    becas_handler,
    buscar_handler,
    callback_dispatcher,
    cdmx_handler,
    cobertura_100_handler,
    guardar_filtro_comando,
    help_handler,
    nuevas_handler,
    prepa_handler,
    start_handler,
    universidad_handler,
)
from bot.middlewares.rate_limit import verificar_limite
from bot.middlewares.tracking import registrar_interaccion
from bot.utils.messages import MENSAJE_RATE_LIMIT

logger = logging.getLogger(__name__)


def with_middlewares(handler):
    """Aplica tracking y rate limiting antes del handler real."""

    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        if not update.effective_user:
            return await handler(update, context)

        user_id = update.effective_user.id

        accion = "desconocido"

        if update.message and update.message.text:
            accion = update.message.text.split()[0]

        elif update.callback_query:
            accion = f"btn:{update.callback_query.data}"

        registrar_interaccion(user_id, accion)

        config = get_bot_config()

        if verificar_limite(user_id, config):
            if update.message:
                await update.message.reply_text(
                    MENSAJE_RATE_LIMIT
                )

            elif update.callback_query:
                await update.callback_query.answer(
                    MENSAJE_RATE_LIMIT,
                    show_alert=True,
                )

            return

        return await handler(update, context)

    return wrapper


async def manejador_global_errores(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """Registra errores no manejados y muestra un mensaje seguro."""

    logger.error(
        "Excepción no manejada mientras se procesaba un update:",
        exc_info=context.error,
    )

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Ocurrió un error inesperado en mis circuitos 🤖💥. "
            "Por favor, intenta de nuevo más tarde."
        )


async def post_stop(application: Application) -> None:
    """Cierra el cliente HTTP del backend al detener el bot."""

    api_client: httpx.AsyncClient | None = application.bot_data.get(
        "api_client"
    )

    if api_client is not None:
        await api_client.aclose()
        logger.info(
            "Cliente HTTP del backend cerrado correctamente."
        )


def build_application(config: BotSettings) -> Application:
    """Construye la aplicación completa de Telegram."""

    # Request HTTP para Telegram.
    telegram_request = (
        __import__(
            "telegram.request",
            fromlist=["HTTPXRequest"],
        ).HTTPXRequest(
            connect_timeout=30.0,
            read_timeout=30.0,
            write_timeout=30.0,
            pool_timeout=30.0,
            proxy=None,
        )
    )

    application = (
        ApplicationBuilder()
        .token(config.TELEGRAM_BOT_TOKEN)
        .request(telegram_request)
        .post_stop(post_stop)
        .build()
    )

    # Cliente HTTP del bot para comunicarse con FastAPI.
    # trust_env=False evita que variables de proxy del sistema
    # interfieran con la conexión local al backend.
    api_client = httpx.AsyncClient(
        base_url=config.BACKEND_API_URL,
        headers={
            "X-API-Key": config.BACKEND_API_KEY,
        },
        timeout=10.0,
        follow_redirects=True,
        trust_env=False,
    )

    application.bot_data["api_client"] = api_client
    application.bot_data["config"] = config

    application.add_handler(
        CommandHandler(
            "start",
            with_middlewares(start_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "ayuda",
            with_middlewares(help_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "becas",
            with_middlewares(becas_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "prepa",
            with_middlewares(prepa_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "universidad",
            with_middlewares(universidad_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "100",
            with_middlewares(cobertura_100_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "cdmx",
            with_middlewares(cdmx_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "nuevas",
            with_middlewares(nuevas_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "buscar",
            with_middlewares(buscar_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "alertas",
            with_middlewares(alertas_handler),
        )
    )

    application.add_handler(
        CommandHandler(
            "filtro",
            with_middlewares(guardar_filtro_comando),
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            with_middlewares(callback_dispatcher)
        )
    )

    application.add_error_handler(
        manejador_global_errores
    )

    return application