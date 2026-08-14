import json
import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.messages import mensaje_alertas_activadas

logger = logging.getLogger(__name__)

async def alertas_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    api_client: httpx.AsyncClient = context.bot_data["api_client"]
    
    try:
        # Obtener estado actual
        resp = await api_client.get(f"/webhooks/usuario/{user.id}")
        resp.raise_for_status()
        estado_actual = resp.json().get("alertas_activas", False)
        
        nuevo_estado = not estado_actual
        
        # Actualizar
        response = await api_client.post(
            "/webhooks/usuario",
            json={"telegram_user_id": user.id, "alertas_activas": nuevo_estado}
        )
        
        await update.message.reply_text(mensaje_alertas_activadas(nuevo_estado))
        
    except httpx.HTTPError as e:
        logger.error(f"Error gestionando alertas para {user.id}: {e}")
        await update.message.reply_text("No pude conectarme al servidor para configurar tus alertas. Intenta en un momento.")

async def guardar_filtro_backend(user_id: int, api_client: httpx.AsyncClient, filtros_dict: dict) -> bool:
    try:
        filtros_str = json.dumps(filtros_dict) if filtros_dict else None
        response = await api_client.post(
            "/webhooks/usuario",
            json={"telegram_user_id": user_id, "filtros_guardados": filtros_str}
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError as e:
        logger.error(f"Error guardando filtro para {user_id}: {e}")
        return False

async def guardar_filtro_comando(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    api_client: httpx.AsyncClient = context.bot_data["api_client"]
    
    # Parsear args formato clave=valor (ej. /filtro nivel_educativo=universidad)
    filtros = {}
    for arg in context.args:
        if "=" in arg:
            k, v = arg.split("=", 1)
            # Manejo bÃ¡sico de bools
            if v.lower() == "true": v = True
            elif v.lower() == "false": v = False
            filtros[k] = v
            
    exito = await guardar_filtro_backend(user.id, api_client, filtros)
    if exito:
        await update.message.reply_text("âœ… Tu preferencia de bÃºsqueda ha sido guardada. Te enviarÃ© notificaciones basadas en este filtro si tienes /alertas activas.")
    else:
        await update.message.reply_text("âŒ No pude guardar tu preferencia. Intenta de nuevo mÃ¡s tarde.")
