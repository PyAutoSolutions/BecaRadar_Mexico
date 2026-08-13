import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.inline import teclado_menu_principal
from bot.utils.messages import MENSAJE_BIENVENIDA

logger = logging.getLogger(__name__)

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    api_client: httpx.AsyncClient = context.bot_data["api_client"]
    
    # Registro silencioso (upsert) en el backend
    try:
        await api_client.post(
            "/webhooks/usuario",
            json={
                "telegram_user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
            }
        )
    except httpx.HTTPError as e:
        logger.warning(f"Error al registrar usuario {user.id} en backend: {e}. Continuando...")

    # Mensaje de bienvenida con menú principal
    await update.message.reply_text(
        MENSAJE_BIENVENIDA,
        reply_markup=teclado_menu_principal()
    )