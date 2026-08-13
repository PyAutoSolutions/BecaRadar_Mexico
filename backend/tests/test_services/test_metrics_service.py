from datetime import UTC, datetime

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
from app.db.models.log_scraper import (
    EstadoScraper,
    FuenteScraper,
    LogScraper,
)
from app.services.metrics_service import MetricsService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def crear_db_en_memoria() -> tuple:
    """Crea una base SQLite en memoria aislada para las pruebas."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    return engine, TestingSessionLocal()


def crear_institucion(
    db: Session,
    nombre: str = "Institución Metrics Test",
) -> Institucion:
    """Crea una institución de prueba."""
    institucion = Institucion(
        nombre=nombre,
        tipo=TipoInstitucion.universidad_publica,
        sitio_web="https://example.com/",
    )

    db.add(institucion)
    db.flush()

    return institucion


def crear_beca(
    db: Session,
    institucion_id: int,
    nombre: str,
    nivel: NivelEducativo = NivelEducativo.universidad,
    estado: EstadoBeca = EstadoBeca.abierta,
) -> Beca:
    """Crea una beca de prueba."""
    beca = Beca(
        nombre=nombre,
        institucion_id=institucion_id,
        tipo=TipoBeca.academica,
        cobertura="Apoyo económico",
        nivel_educativo=nivel,
        requisitos="Cumplir requisitos.",
        estado=estado,
        link_oficial=f"https://example.com/{nombre.lower().replace(' ', '-')}",
        fuente_scraper="test",
        hash_contenido=f"hash-{nombre}",
        ultima_verificacion=datetime.now(UTC).replace(tzinfo=None),
    )

    db.add(beca)
    db.flush()

    return beca


def crear_log_scraper(
    db: Session,
    fuente: FuenteScraper,
    estado: EstadoScraper,
    becas_encontradas: int = 0,
    becas_nuevas: int = 0,
    becas_actualizadas: int = 0,
) -> LogScraper:
    """Crea un registro de ejecución del scraper."""
    log = LogScraper(
        fuente=fuente,
        estado=estado,
        becas_encontradas=becas_encontradas,
        becas_nuevas=becas_nuevas,
        becas_actualizadas=becas_actualizadas,
        errores=None,
        duracion_segundos=1.25,
        fecha_ejecucion=datetime.now(UTC).replace(tzinfo=None),
    )

    db.add(log)
    db.flush()

    return log


def test_resumen_general_cuenta_becas_instituciones_y_niveles() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        crear_beca(
            db,
            institucion.id,
            "Beca Prepa Metrics",
            nivel=NivelEducativo.preparatoria,
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Universidad Metrics 1",
            nivel=NivelEducativo.universidad,
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Universidad Metrics 2",
            nivel=NivelEducativo.universidad,
        )

        db.commit()

        service = MetricsService(db)
        resultado = service.resumen_general()

        assert resultado["total_becas_activas"] == 3
        assert resultado["total_instituciones"] == 1

        desglose = resultado["desglose_niveles"]

        assert desglose["preparatoria"] == 1
        assert desglose["universidad"] == 2

    finally:
        db.close()
        engine.dispose()


def test_resumen_general_no_cuenta_becas_cerradas_como_activas() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        crear_beca(
            db,
            institucion.id,
            "Beca Abierta Metrics",
            estado=EstadoBeca.abierta,
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Cerrada Metrics",
            estado=EstadoBeca.cerrada,
        )

        db.commit()

        service = MetricsService(db)
        resultado = service.resumen_general()

        assert resultado["total_becas_activas"] == 1

    finally:
        db.close()
        engine.dispose()


def test_resumen_general_sin_corridas_devuelve_ultima_corrida_none() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        crear_beca(
            db,
            institucion.id,
            "Beca Sin Scraper Metrics",
        )

        db.commit()

        service = MetricsService(db)
        resultado = service.resumen_general()

        assert resultado.get("ultima_corrida_scraper") is None

    finally:
        db.close()
        engine.dispose()


def test_resumen_general_incluye_ultima_corrida_scraper() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        crear_beca(
            db,
            institucion.id,
            "Beca Con Scraper Metrics",
        )

        crear_log_scraper(
            db,
            fuente=FuenteScraper.benito_juarez,
            estado=EstadoScraper.exito,
            becas_encontradas=10,
            becas_nuevas=2,
            becas_actualizadas=3,
        )

        db.commit()

        service = MetricsService(db)
        resultado = service.resumen_general()

        ultima = resultado["ultima_corrida_scraper"]

        assert ultima is not None
        assert ultima["estado"] == "exito"

    finally:
        db.close()
        engine.dispose()


def test_historial_scraper_devuelve_registros_mas_recientes() -> None:
    engine, db = crear_db_en_memoria()

    try:
        crear_log_scraper(
            db,
            fuente=FuenteScraper.benito_juarez,
            estado=EstadoScraper.exito,
            becas_encontradas=5,
            becas_nuevas=1,
        )

        crear_log_scraper(
            db,
            fuente=FuenteScraper.unam,
            estado=EstadoScraper.exito,
            becas_encontradas=8,
            becas_nuevas=2,
        )

        crear_log_scraper(
            db,
            fuente=FuenteScraper.ipn,
            estado=EstadoScraper.error,
            becas_encontradas=0,
            becas_nuevas=0,
        )

        db.commit()

        service = MetricsService(db)

        historial = service.historial_scraper(limit=2)

        assert len(historial) == 2
        assert all(
            isinstance(registro, LogScraper)
            for registro in historial
        )

    finally:
        db.close()
        engine.dispose()


def test_tasa_exito_scraper_calcula_porcentaje() -> None:
    engine, db = crear_db_en_memoria()

    try:
        crear_log_scraper(
            db,
            fuente=FuenteScraper.benito_juarez,
            estado=EstadoScraper.exito,
        )

        crear_log_scraper(
            db,
            fuente=FuenteScraper.unam,
            estado=EstadoScraper.exito,
        )

        crear_log_scraper(
            db,
            fuente=FuenteScraper.ipn,
            estado=EstadoScraper.error,
        )

        crear_log_scraper(
            db,
            fuente=FuenteScraper.tec,
            estado=EstadoScraper.error,
        )

        db.commit()

        service = MetricsService(db)

        tasa = service.tasa_exito_scraper(ultimas_n=4)

        assert tasa == 50.0

    finally:
        db.close()
        engine.dispose()


def test_tasa_exito_scraper_sin_registros_devuelve_none() -> None:
    engine, db = crear_db_en_memoria()

    try:
        service = MetricsService(db)

        tasa = service.tasa_exito_scraper(ultimas_n=20)

        assert tasa is None

    finally:
        db.close()
        engine.dispose()