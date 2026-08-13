import logging

import httpx
from telegram import Update
from telegram.ext import ContextTypes

from bot.keyboards.inline import teclado_guardar_filtro
from bot.utils.formatters import formatear_lista_becas
from bot.utils.messages import MENSAJE_ERROR_BACKEND, MENSAJE_SIN_RESULTADOS

logger = logging.getLogger(__name__)

async def buscar_y_mostrar(update: Update, context: ContextTypes.DEFAULT_TYPE, filtros: dict) -> None:
    """Función central compartida por comandos y botones inline para buscar becas."""
    api_client: httpx.AsyncClient = context.bot_data["api_client"]
    
    # Límite fijo por paginación para Telegram
    params = {**filtros, "limit": 5}
    
    try:
        response = await api_client.get("/becas", params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        
        message_func = update.message.reply_text if update.message else update.callback_query.message.reply_text
        
        if not items:
            await message_func(MENSAJE_SIN_RESULTADOS)
            return
            
        texto_respuesta = formatear_lista_becas(items)
        
        # Enviar resultados y ofrecer guardar la búsqueda (si aplica)
        # Omitimos teclado de guardar si el filtro fue por texto libre ("q")
        reply_markup = teclado_guardar_filtro(filtros) if "q" not in filtros else None
        
        await message_func(texto_respuesta, reply_markup=reply_markup, disable_web_page_preview=True)
        
    except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
        logger.error(f"Error consultando al backend en búsqueda: {e}")
        message_func = update.message.reply_text if update.message else update.callback_query.message.reply_text
        await message_func(MENSAJE_ERROR_BACKEND)

async def becas_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await buscar_y_mostrar(update, context, {})

async def prepa_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await buscar_y_mostrar(update, context, {"nivel_educativo": "preparatoria"})

async def universidad_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await buscar_y_mostrar(update, context, {"nivel_educativo": "universidad"})

async def cobertura_100_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await buscar_y_mostrar(update, context, {"cobertura_100": True})

async def cdmx_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await buscar_y_mostrar(update, context, {"ubicacion": "CDMX"})

async def nuevas_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await buscar_y_mostrar(update, context, {"nuevas_dias": 30})

async def buscar_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("🔎 Por favor incluye lo que buscas. Ejemplo:\n/buscar posgrado en sistemas")
        return
    query = " ".join(context.args)
    await buscar_y_mostrar(update, context, {"q": query})