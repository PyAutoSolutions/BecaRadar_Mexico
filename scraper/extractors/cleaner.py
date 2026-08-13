import hashlib
import re

from scraper.extractors.dates import parsear_fecha_es


def limpiar_texto(texto: str) -> str:
    """Elimina espacios extra, saltos de línea múltiples y entidades HTML comunes."""
    if not texto:
        return ""
    # Reemplazar NBSP
    t = texto.replace("&nbsp;", " ").replace("\xa0", " ")
    # Colapsar múltiples espacios y saltos de línea a un solo espacio
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

def normalizar_nombre_institucion(nombre_raw: str) -> str:
    """Convierte variantes conocidas en formas canónicas únicas para evitar duplicados en DB."""
    n = limpiar_texto(nombre_raw).lower()
    
    if "unam" in n or "nacional autónoma" in n or "nacional autonoma" in n:
        return "UNAM"
    if "ipn" in n or "politécnico" in n or "politecnico" in n:
        return "IPN"
    if "tec" in n and ("monterrey" in n or "itesm" in n):
        return "Tecnológico de Monterrey"
    if "gobierno" in n or "benito" in n:
        return "Gobierno Federal"
        
    # Si no hay match explícito, se retorna limpio capitalizado (Title Case)
    return limpiar_texto(nombre_raw).title()

def calcular_hash(beca_dict: dict) -> str:
    """Calcula SHA-1 del contenido core para detectar si la beca fue actualizada."""
    # Concatenamos los campos que si cambian, justifican un UPDATE
    contenido = f"{beca_dict['nombre']}|{beca_dict['fecha_limite']}|{beca_dict['cobertura']}|{beca_dict['requisitos']}"
    return hashlib.sha1(contenido.encode("utf-8")).hexdigest()

def limpiar_beca_raw(raw: dict) -> dict | None:
    """
    Toma un dict crudo devuelto por una Fuente, limpia y estandariza sus campos,
    y calcula el hash. Retorna None si el registro es inválido (ej. sin nombre).
    """
    nombre = limpiar_texto(raw.get("nombre_raw", ""))
    if not nombre:
        return None

    institucion_nombre = normalizar_nombre_institucion(raw.get("institucion_raw", ""))
    
    # Normalizar nivel (simplificado para MVP)
    nivel_raw = limpiar_texto(raw.get("nivel_educativo_raw", "")).lower()
    nivel_final = "preparatoria"
    if "uni" in nivel_raw or "lic" in nivel_raw or "superior" in nivel_raw:
        nivel_final = "universidad"
    elif "pos" in nivel_raw or "maes" in nivel_raw:
        nivel_final = "posgrado"

    fecha_apertura = parsear_fecha_es(raw.get("fecha_apertura_raw", ""))
    fecha_limite = parsear_fecha_es(raw.get("fecha_limite_raw", ""))

    beca_limpia = {
        "nombre": nombre,
        "institucion_nombre": institucion_nombre,
        "nivel_educativo": nivel_final,
        "cobertura": limpiar_texto(raw.get("cobertura_raw", "")),
        "cobertura_100": raw.get("cobertura_100", False),
        "requisitos": limpiar_texto(raw.get("requisitos_raw", "")),
        "link_oficial": limpiar_texto(raw.get("link_raw", "")),
        "fecha_apertura": fecha_apertura.isoformat() if fecha_apertura else None,
        "fecha_limite": fecha_limite.isoformat() if fecha_limite else None,
        "activa": True
    }

    # Calculamos el hash e inyectamos al diccionario final
    beca_limpia["hash_contenido"] = calcular_hash(beca_limpia)
    
    return beca_limpia