# Arquitectura General de BecaRadar México

BecaRadar México es una plataforma diseñada para centralizar, estructurar y difundir convocatorias de becas académicas en México. Se compone de 4 servicios desacoplados que interactúan a través de una base de datos central PostgreSQL y APIs REST HTTP.

```text
┌─────────────────┐       ┌─────────────────┐
│ Scraper Cron    │       │ Bot Telegram    │
│ (Python/BS4)    │       │ (python-telegram)│
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ Writes Direct           │ HTTP / REST
         ▼                         ▼
┌───────────────────────────────────────────┐
│          PostgreSQL Database              │
└───────────────────────────────────────────┘
         ▲
         │ HTTP / REST
┌────────┴────────┐
│ Frontend Web    │
│ (React + Vite)  │
└─────────────────┘

```

## 1. Componentes del Sistema

### A. Backend (FastAPI)

* **Rol:** Proveer endpoints RESTful de lectura para clientes públicos (Bot, Frontend) y métricas de monitoreo.
* **Tecnologías:** Python 3.11, FastAPI, SQLAlchemy, Pydantic, Alembic.
* **Seguridad:** CORS abierto (`*`) para consultas públicas, restricción por API Key opcional en rutas administrativas.

### B. Bot de Telegram

* **Rol:** Interfaz conversacional directa para estudiantes.
* **Tecnologías:** `python-telegram-bot` v20+ (modo polling).
* **Estrategia:** Consume la API del Backend de forma síncrona/asíncrona mediante `httpx`. Registra interacciones de usuarios en la tabla `usuarios_bot`.

### C. Scraper Pipeline

* **Rol:** Extraer, limpiar y actualizar becas desde portales gubernamentales e institucionales (UNAM, IPN, Tec, Benito Juárez).
* **Tecnologías:** Requests, BeautifulSoup4, Regex.
* **Estrategia de Idempotencia:** Utiliza un hash SHA-1 (`hash_contenido`) generado a partir del contenido de la beca para evitar actualizaciones redundantes en la base de datos.

### D. Frontend Web

* **Rol:** Panel de consulta visual e interactivo para usuarios que prefieren la Web.
* **Tecnologías:** React, Vite, Tailwind CSS.

---

## 2. Decisión de Diseño Clave

* **Sin duplicación de esquema:** El Scraper y el Bot comparten las mismas definiciones de modelos de SQLAlchemy (`backend.app.db.models`) que el Backend, garantizando coherencia sin importar el punto de origen.