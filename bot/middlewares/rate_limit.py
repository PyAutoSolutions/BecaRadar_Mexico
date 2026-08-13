import time

from bot.core.config import BotSettings

# Diccionario en memoria: telegram_user_id -> lista de timestamps
_historial: dict[int, list[float]] = {}

def verificar_limite(telegram_user_id: int, config: BotSettings) -> bool:
    """
    Retorna True si el usuario excedió el límite y debe ser bloqueado, False de lo contrario.
    Usa el algoritmo de 'Sliding Window'.
    """
    ahora = time.time()
    
    if telegram_user_id not in _historial:
        _historial[telegram_user_id] = [ahora]
        return False
        
    timestamps = _historial[telegram_user_id]
    
    # Limpiar timestamps viejos fuera de la ventana
    ventana_valida = ahora - config.RATE_LIMIT_VENTANA_SEGUNDOS
    timestamps = [ts for ts in timestamps if ts > ventana_valida]
    
    if len(timestamps) >= config.RATE_LIMIT_MENSAJES:
        _historial[telegram_user_id] = timestamps
        return True # Excedió
        
    timestamps.append(ahora)
    _historial[telegram_user_id] = timestamps
    return False