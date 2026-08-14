import json

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.filters import guardar_filtro_backend
from bot.handlers.search import buscar_y_mostrar


async def callback_dispatcher(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    
    # Obligatorio para Telegram: confirmar recepciÃ³n
    await query.answer()
    
    # Formato esperado: "accion:parametro" o "accion"
    accion, _, parametro = query.data.partition(":")
    
    if accion == "filtro":
        filtros = {}
        if parametro == "prepa":
            filtros = {"nivel_educativo": "preparatoria"}
        elif parametro == "universidad":
            filtros = {"nivel_educativo": "preparatoria"}
        elif parametro == "100":
            filtros = {"cobertura_100": True}
        elif parametro == "nuevas":
            filtros = {"nuevas_dias": 30}
            
        await buscar_y_mostrar(update, context, filtros)
        
    elif accion == "guardar_filtro":
        # Deserializar filtro adjunto al botÃ³n
        filtros_dict = {}
        if parametro:
            try:
                filtros_dict = json.loads(parametro)
            except json.JSONDecodeError:
                pass
                
        user_id = query.from_user.id
        api_client = context.bot_data["api_client"]
        
        exito = await guardar_filtro_backend(user_id, api_client, filtros_dict)
        if exito:
            await query.message.reply_text("âœ… Filtro guardado como favorito.")
        else:
            await query.message.reply_text("âŒ Error al guardar el filtro.")
            
    else:
        # En caso de callbacks viejos que ya no coincidan con la lÃ³gica
        await query.message.reply_text("Este botÃ³n ya no es vÃ¡lido, usa /becas para una bÃºsqueda nueva.")
