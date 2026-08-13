#!/usr/bin/env bash
set -e

echo "=== Configurando entorno de desarrollo de BecaRadar México ==="

# 1. Crear entorno virtual Python
if [ ! -d ".venv" ]; then
    echo "-> Creando entorno virtual .venv..."
    python3 -m venv .venv
else
    echo "-> Entorno virtual .venv ya existe."
fi

source .venv/bin/activate

# 2. Instalar dependencias Python (Editable mode raíz)
echo "-> Instalando paquetes de Python..."
pip install --upgrade pip
pip install -e .

# 3. Instalar dependencias del Frontend
echo "-> Instalando dependencias de Node.js en frontend..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    cd ..
fi

# 4. Copiar variables de entorno iniciales si no existen
if [ ! -f ".env.development" ]; then
    echo "-> Generando .env.development inicial desde .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env.development
    else
        echo "DATABASE_URL=postgresql://beca_user:beca_pass@localhost:5432/becaradar_db" > .env.development
        echo "TELEGRAM_BOT_TOKEN=tu_token_aqui" >> .env.development
    fi
fi

echo "=== Setup completado con éxito ==="
echo "Próximos pasos:"
echo "1. Edita .env.development con tus credenciales reales"
echo "2. Levanta PostgreSQL (o ejecuta docker-compose up db -d)"
echo "3. Ejecuta migraciones: alembic upgrade head"
echo "4. Siembras datos iniciales: python scripts/seed_data.py"