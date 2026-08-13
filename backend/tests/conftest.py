import os
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Variables de entorno aisladas para los tests.
# Se establecen antes de importar app.main.
# ---------------------------------------------------------------------------

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///:memory:",
)

os.environ.setdefault(
    "SECRET_API_KEY",
    "test-secret-api-key",
)

os.environ.setdefault(
    "BACKEND_API_KEY",
    "test-backend-api-key",
)

os.environ.setdefault(
    "BACKEND_API_URL",
    "http://testserver/api/v1",
)

os.environ.setdefault(
    "TELEGRAM_BOT_TOKEN",
    "1234567890:TEST_TOKEN_FOR_PYTEST",
)

os.environ.setdefault(
    "CORS_ORIGINS",
    '["*"]',
)

os.environ.setdefault(
    "ENVIRONMENT",
    "test",
)

os.environ.setdefault(
    "LOG_LEVEL",
    "WARNING",
)

os.environ.setdefault(
    "RATE_LIMIT_MENSAJES",
    "5",
)

os.environ.setdefault(
    "RATE_LIMIT_VENTANA_SEGUNDOS",
    "10",
)


from app.db.base import Base
from app.db.models.beca import (
    Beca,
    EstadoBeca,
    NivelEducativo,
    TipoBeca,
)
from app.db.models.institucion import (
    Institucion,
    TipoInstitucion,
)
from app.db.session import get_db
from app.main import app


@pytest.fixture(scope="function")
def db_session() -> Session:
    """
    Crea una SQLite en memoria compartida por todas las conexiones
    utilizadas durante una prueba.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.rollback()
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    TestClient de FastAPI usando exactamente la misma sesión de prueba.
    """

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def sample_institucion(db_session: Session) -> Institucion:
    """
    Institución de ejemplo.
    """
    institucion = Institucion(
        nombre="UNAM de Prueba",
        tipo=TipoInstitucion.universidad_publica,
        sitio_web="https://www.unam.mx/",
    )

    db_session.add(institucion)
    db_session.commit()
    db_session.refresh(institucion)

    return institucion


@pytest.fixture
def sample_beca(
    db_session: Session,
    sample_institucion: Institucion,
) -> Beca:
    """
    Beca de ejemplo.
    """
    beca = Beca(
        nombre="Beca Excelencia Prueba",
        institucion_id=sample_institucion.id,
        tipo=TipoBeca.academica,
        cobertura="100%",
        nivel_educativo=NivelEducativo.universidad,
        requisitos="Promedio de 9.0",
        ubicacion="CDMX",
        fecha_apertura=datetime.now(UTC).date(),
        fecha_limite=datetime.now(UTC).date(),
        estado=EstadoBeca.abierta,
        link_oficial="https://www.unam.mx/",
        fuente_scraper="manual",
        hash_contenido="hash_prueba_123",
        ultima_verificacion=datetime.now(UTC).replace(tzinfo=None),
    )

    db_session.add(beca)
    db_session.commit()
    db_session.refresh(beca)

    return beca