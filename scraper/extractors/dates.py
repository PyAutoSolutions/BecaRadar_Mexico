import logging
import re
from datetime import date

logger = logging.getLogger(__name__)

MESES_ES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

# Patrón 1: "28 de Febrero de 2027" o "28 de febrero del 2027"
REGEX_FORMATO_LARGO = re.compile(
    r"(\d{1,2})\s+de\s+([a-zA-Z]+)(?:\s+del?\s+)(\d{4})"
)

# Patrón 2: numérico con slash o guion: "15/05/2026", "15-05-2026"
REGEX_NUMERICO = re.compile(
    r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})"
)

FRASES_SIN_FECHA = [
    "agotar cupo", "próximamente", "proximamente",
    "por confirmar", "por definir", "convocatoria anual continua",
    "verificar calendario", "revisar proceso"
]

def parsear_fecha_es(texto: str) -> date | None:
    if not texto:
        return None
        
    texto_limpio = texto.lower().strip()
    
    # 1. Revisar frases conocidas sin fecha exacta
    for frase in FRASES_SIN_FECHA:
        if frase in texto_limpio:
            return None

    # 2. Intentar formato largo (ej. 28 de febrero de 2027)
    match_largo = REGEX_FORMATO_LARGO.search(texto_limpio)
    if match_largo:
        dia, mes_str, anio = match_largo.groups()
        if mes_str in MESES_ES:
            try:
                return date(int(anio), MESES_ES[mes_str], int(dia))
            except ValueError:
                pass # Fecha inválida tipo 31 de febrero

    # 3. Intentar formato numérico (ej. 15/05/2026)
    match_num = REGEX_NUMERICO.search(texto_limpio)
    if match_num:
        dia, mes, anio = match_num.groups()
        try:
            return date(int(anio), int(mes), int(dia))
        except ValueError:
            pass

    # No se reconoció el formato
    logger.debug(f"Formato de fecha no reconocido, se degrada a None: '{texto}'")
    return None