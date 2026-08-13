MENSAJE_BIENVENIDA = """
¡Hola! 👋 Soy **BecaRadar**, tu asistente para no perderte ninguna beca en México.

Puedo ayudarte a encontrar oportunidades rápidamente. Selecciona una opción del menú o escribe `/ayuda` para ver todo lo que puedo hacer.
"""

MENSAJE_AYUDA = """
Aquí tienes todo lo que puedo hacer por ti:

/becas - 🎓 Muestra las últimas 5 becas generales.
/prepa - 🎒 Becas para nivel medio superior.
/universidad - 🏫 Becas para licenciatura.
/100 - 💵 Becas con cobertura completa (100%).
/cdmx - 📍 Becas específicas de la Ciudad de México.
/nuevas - ✨ Becas publicadas en los últimos 30 días.
/buscar [texto] - 🔎 Busca por palabra clave (ej: `/buscar ingenieria`).
/alertas - 🔔 Activa o desactiva las notificaciones automáticas.
/ayuda - ℹ️ Muestra este mensaje.
"""

MENSAJE_SIN_RESULTADOS = "🤷‍♂️ No encontré becas activas con esos filtros en este momento. ¡Intenta con otra búsqueda!"

MENSAJE_ERROR_BACKEND = "🔌 Oops, no pude conectarme al servidor de becas ahorita. Dame unos minutitos e intenta de nuevo."

MENSAJE_RATE_LIMIT = "⏳ ¡Wow, vas muy rápido! Espera unos segundos antes de enviar más comandos."

def mensaje_alertas_activadas(activas: bool) -> str:
    if activas:
        return "🔔 ¡Alertas ACTIVADAS! Te avisaré cuando encuentre becas nuevas o estén por vencer."
    return "🔕 Alertas DESACTIVADAS. Ya no te molestaré, puedes buscar manualmente cuando gustes."