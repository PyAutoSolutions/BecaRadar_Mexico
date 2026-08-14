BecaRadar México 🟢📣

""CI" (https://github.com/PyAutoSolutions/BecaRadar_Mexico/actions/workflows/ci.yml/badge.svg)" (https://github.com/PyAutoSolutions/BecaRadar_Mexico/actions/workflows/ci.yml)

BecaRadar México es un sistema automatizado que rastrea, estandariza y notifica convocatorias de becas vigentes en México mediante una API, scrapers y un bot de Telegram.

🤖 Bot en vivo: "@BecaRadarMX_bot" (https://t.me/BecaRadarMX_bot)

Requisitos

- Python 3.11+
- Node.js y npm
- Docker Desktop
- Git

1. Clonar el proyecto

git clone https://github.com/PyAutoSolutions/BecaRadar_Mexico.git
cd BecaRadar_Mexico

2. Configuración

Crea o completa el archivo:

.env.development

No subas secretos al repositorio.

Variables importantes:

TELEGRAM_BOT_TOKEN=...
SECRET_API_KEY=...
BACKEND_API_KEY=...
DATABASE_URL=...

3. Backend local

Desde la raíz:

$env:PYTHONPATH="backend;."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

API:

http://localhost:8000

Health:

http://localhost:8000/health

Swagger:

http://localhost:8000/docs

4. Bot Telegram local

En otra terminal:

cd "C:\Users\Lenovo\Downloads\BecaRadar_Mexico (1)\BecaRadar_Mexico"
$env:PYTHONPATH="backend;."
.\.venv\Scripts\python.exe -m bot.main

No ejecutes dos instancias del bot al mismo tiempo.

5. Scraper local

En otra terminal:

cd "C:\Users\Lenovo\Downloads\BecaRadar_Mexico (1)\BecaRadar_Mexico"
$env:PYTHONPATH="backend;."
.\.venv\Scripts\python.exe -m scraper.main

6. Frontend

Desde la carpeta "frontend":

cd frontend
npm install
npm run dev

Vite normalmente utiliza:

http://localhost:5173/

Si ese puerto está ocupado, Vite puede elegir automáticamente otro puerto libre, por ejemplo "5175".

7. Docker

Verificar:

docker --version
docker compose version

Construir las imágenes:

docker compose build

Levantar backend y bot:

docker compose up -d backend bot

Ver estado:

docker compose ps

Ejecutar scraper:

docker compose run --rm scraper

Ver logs:

docker compose logs --tail=100 backend
docker compose logs --tail=100 bot

8. Base de datos y migraciones

Migraciones locales:

cd backend
..\.venv\Scripts\python.exe -m alembic upgrade head
cd ..

Migraciones en Docker:

docker compose exec backend python -m alembic upgrade head

9. Tests y calidad

Ejecutar todos los tests:

.\.venv\Scripts\python.exe -m pytest backend/tests -v

Ejecutar Ruff:

.\.venv\Scripts\python.exe -m ruff check .

Comprobar la compilación de Python:

.\.venv\Scripts\python.exe -m compileall -q backend bot scraper scripts

10. Makefile

El proyecto contiene estas tareas:

make dev
make scrape
make migrate
make test
make seed
make metrics
make logs

En Windows puede ser necesario ejecutar directamente los comandos equivalentes si "make" no está instalado.

11. API principal

Endpoints principales:

GET /health
GET /api/v1/becas/
GET /api/v1/stats/resumen
GET /docs

Ejemplos:

/api/v1/becas/?limit=5
/api/v1/becas/?nivel_educativo=preparatoria&limit=5
/api/v1/becas/?nivel_educativo=universidad&limit=5
/api/v1/becas/?cobertura_100=true&limit=5
/api/v1/becas/?nuevas_dias=30&limit=5

12. Bot Telegram

Comandos principales:

/start
/ayuda
/becas
/prepa
/universidad
/100
/cdmx
/nuevas
/buscar [texto]
/alertas

El bot también permite guardar filtros favoritos.

13. Scrapers

Fuentes actualmente implementadas:

- Benito Juárez
- UNAM
- IPN
- Tecnológico de Monterrey

14. Seguridad

No subas al repositorio:

.env
.env.development
.env.production
*.db
*.jsonl
*.pyc
__pycache__/
.venv/
node_modules/
frontend/dist/

Los secretos deben configurarse localmente o mediante los secretos de GitHub Actions.

15. GitHub Actions

Workflows:

.github/workflows/ci.yml
.github/workflows/scraper_cron.yml

El workflow del scraper puede ejecutarse manualmente desde GitHub Actions.

16. Estado validado del proyecto

La auditoría realizada verificó:

- Backend funcional
- API funcionando
- Swagger funcionando
- Alembic funcionando
- 53 tests pasando
- Ruff sin errores
- 4 fuentes de scraping
- Bot Telegram funcional
- Docker funcionando
- SQLite compartido entre servicios Docker
- Frontend compilando
- npm audit sin vulnerabilidades
- Git limpio y sincronizado
- ZIP final generado
- ZIP final sin secretos ni archivos temporales

17. Repositorio

https://github.com/PyAutoSolutions/BecaRadar_Mexico