MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio", 
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

def humanizar_fecha(fecha_iso: str) -> str:
    """Convierte '2027-02-28' a '28 de febrero de 2027'."""
    if not fecha_iso:
        return "Sin fecha límite especificada"
    try:
        y, m, d = fecha_iso.split("-")
        return f"{int(d)} de {MESES[int(m)-1]} de {y}"
    except (ValueError, IndexError):
        return fecha_iso

def formatear_beca(beca: dict) -> str:
    """Formatea el diccionario de una beca en un string para Telegram."""
    nombre = beca.get("nombre", "Beca Desconocida")
    
    institucion_obj = beca.get("institucion", {})
    institucion = institucion_obj.get("nombre", "Varias Instituciones")
    
    cobertura = beca.get("cobertura", "No especificada")
    
    # Truncar requisitos para no saturar el mensaje
    requisitos = beca.get("requisitos", "Consulta el enlace oficial.")
    if len(requisitos) > 120:
        requisitos = requisitos[:117] + "..."
        
    fecha_limite = humanizar_fecha(beca.get("fecha_limite"))
    link = beca.get("link_oficial", "Sin enlace")

    return (
        f"📌 **{nombre}**\n"
        f"🏫 {institucion}\n"
        f"💰 {cobertura}\n"
        f"📋 {requisitos}\n"
        f"📅 Cierra: {fecha_limite}\n"
        f"🔗 {link}"
    )

def formatear_lista_becas(becas: list[dict]) -> str:
    """Toma una lista de diccionarios de becas y las une con separadores."""
    if not becas:
        return ""
    
    textos = [formatear_beca(beca) for beca in becas]
    return "\n\n〰️〰️〰️〰️〰️〰️〰️\n\n".join(textos)