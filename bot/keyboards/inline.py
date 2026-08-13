import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def teclado_menu_principal() -> InlineKeyboardMarkup:
    teclado = [
        [
            InlineKeyboardButton("🟦 Prepa", callback_data="filtro:prepa"),
            InlineKeyboardButton("🟧 Universidad", callback_data="filtro:universidad"),
        ],
        [
            InlineKeyboardButton("🟩 100% Cubierto", callback_data="filtro:100"),
            InlineKeyboardButton("🟪 Recientes", callback_data="filtro:nuevas"),
        ]
    ]
    return InlineKeyboardMarkup(teclado)

def teclado_guardar_filtro(filtros: dict) -> InlineKeyboardMarkup:
    # Telegram tiene un límite de 64 bytes para callback_data
    # Se convierte el dict a string comprimido, si es muy largo falla en la API de Telegram,
    # pero nuestros filtros aquí son muy cortos.
    filtro_str = json.dumps(filtros, separators=(',', ':'))
    # "guardar_filtro:..."
    cb_data = f"guardar_filtro:{filtro_str}"
    
    # Si por alguna razón excede (poco probable con estos filtros), se trunca (no guardará props extra)
    if len(cb_data.encode("utf-8")) > 64:
        cb_data = "guardar_filtro:" 
        
    teclado = [
        [InlineKeyboardButton("💾 Guardar como mi filtro favorito", callback_data=cb_data)]
    ]
    return InlineKeyboardMarkup(teclado)