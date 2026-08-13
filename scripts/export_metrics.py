import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
LOGS_DIR = Path("logs")
REPORTES_DIR = Path("reportes")

def obtener_metricas_backend() -> dict:
    resumen = {}
    scraper = {}
    try:
        r_resumen = requests.get(f"{API_BASE_URL}/stats/resumen", timeout=5)
        if r_resumen.status_code == 200:
            resumen = r_resumen.json()
            
        r_scraper = requests.get(f"{API_BASE_URL}/stats/scraper", timeout=5)
        if r_scraper.status_code == 200:
            scraper = r_scraper.json()
    except requests.RequestException as exc:
        print(f"[WARN] No se pudo conectar a la API del backend: {exc}")
        
    return {"resumen": resumen, "scraper": scraper}

def obtener_metricas_uso_bot() -> dict:
    archivo_log = LOGS_DIR / "uso_bot.jsonl"
    if not archivo_log.exists():
        return {"total_interacciones": 0, "comandos": {}}

    total = 0
    comandos_counter = Counter()

    with open(archivo_log, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                total += 1
                cmd = data.get("comando", "desconocido")
                comandos_counter[cmd] += 1
            except json.JSONDecodeError:
                continue

    return {
        "total_interacciones": total,
        "comandos": dict(comandos_counter)
    }

def generar_reporte():
    backend = obtener_metricas_backend()
    bot = obtener_metricas_uso_bot()
    
    REPORTES_DIR.mkdir(exist_ok=True)
    fecha_str = datetime.now(UTC).replace(tzinfo=None).strftime("%Y-%m-%d_%H%M")
    archivo_salida = REPORTES_DIR / f"reporte_evidencia_{fecha_str}.md"

    resumen_db = backend.get("resumen", {})
    scraper_logs = backend.get("scraper", [])

    contenido = f"""# Reporte de Evidencia BecaRadar México
**Fecha de generación:** {datetime.now(UTC).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. Métrica de Base de Datos (Backend API)
- **Total de Becas Activas:** {resumen_db.get('total_becas', 'N/A')}
- **Desglose por Nivel Educativo:**
  - Preparatoria: {resumen_db.get('por_nivel', {}).get('preparatoria', 0)}
  - Universidad: {resumen_db.get('por_nivel', {}).get('universidad', 0)}
  - Posgrado: {resumen_db.get('por_nivel', {}).get('posgrado', 0)}
- **Becas Cobertura 100%:** {resumen_db.get('cobertura_100', 'N/A')}

---

## 2. Métricas de Uso del Bot de Telegram (Log Local)
- **Total de Interacciones Registradas:** {bot['total_interacciones']}
- **Comandos ejecutados:**
"""
    for cmd, count in bot['comandos'].items():
        contenido += f"  - `{cmd}`: {count}\n"

    contenido += """
---

## 3. Estado Reciente de Scrapers (Últimas Ejecuciones)
| Fuente | Estado | Nuevas | Actualizadas | Duración (s) | Fecha |
|---|---|---|---|---|---|
"""
    for log in scraper_logs:
        contenido += f"| {log.get('fuente')} | {log.get('estado')} | {log.get('becas_nuevas')} | {log.get('becas_actualizadas')} | {log.get('duracion_segundos')} | {log.get('creado_en')} |\n"

    with open(archivo_salida, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f" Reporte de evidencia generado exitosamente en: {archivo_salida}")

if __name__ == "__main__":
    generar_reporte()