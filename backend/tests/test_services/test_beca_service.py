from datetime import UTC, datetime

from app.core.exceptions import BecaNotFoundException
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
from app.schemas.beca import BecaFiltros
from app.services.beca_service import BecaService
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def crear_db_en_memoria() -> tuple:
    """Crea una SQLite en memoria aislada para cada prueba."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )

    return engine, TestingSessionLocal()


def crear_institucion(
    db: Session,
    nombre: str = "Institución Test",
    tipo: TipoInstitucion = TipoInstitucion.universidad_publica,
) -> Institucion:
    """Crea y persiste una institución de prueba."""
    institucion = Institucion(
        nombre=nombre,
        tipo=tipo,
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
    cobertura: str = "Apoyo económico",
    estado: EstadoBeca = EstadoBeca.abierta,
) -> Beca:
    """Crea y persiste una beca de prueba."""
    beca = Beca(
        nombre=nombre,
        institucion_id=institucion_id,
        tipo=TipoBeca.academica,
        cobertura=cobertura,
        nivel_educativo=nivel,
        requisitos="Cumplir los requisitos de la convocatoria.",
        ubicacion=None,
        fecha_apertura=None,
        fecha_limite=None,
        estado=estado,
        link_oficial=(
            "https://example.com/"
            f"{nombre.lower().replace(' ', '-')}"
        ),
        fuente_scraper="test",
        hash_contenido=f"hash-{nombre}",
        ultima_verificacion=datetime.now(UTC).replace(tzinfo=None),
    )

    db.add(beca)
    db.flush()

    return beca


def test_buscar_becas_filtra_por_nivel_educativo() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        crear_beca(
            db,
            institucion.id,
            "Beca Prepa Test",
            nivel=NivelEducativo.preparatoria,
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Universidad Test",
            nivel=NivelEducativo.universidad,
        )

        db.commit()

        service = BecaService(db)

        filtros = BecaFiltros(
            nivel_educativo=NivelEducativo.preparatoria,
        )

        items, total = service.buscar_becas(
            filtros,
            skip=0,
            limit=20,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].nombre == "Beca Prepa Test"
        assert (
            items[0].nivel_educativo
            == NivelEducativo.preparatoria
        )

    finally:
        db.close()
        engine.dispose()


def test_buscar_becas_filtra_cobertura_100() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(
            db,
            nombre="Tec Test",
            tipo=TipoInstitucion.universidad_privada,
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Completa Test",
            cobertura="100% de colegiatura",
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Parcial Test",
            cobertura="50% de colegiatura",
        )

        db.commit()

        service = BecaService(db)

        filtros = BecaFiltros(
            cobertura_100=True,
        )

        items, total = service.buscar_becas(
            filtros,
            skip=0,
            limit=20,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].nombre == "Beca Completa Test"

    finally:
        db.close()
        engine.dispose()


def test_buscar_becas_filtra_por_ubicacion() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        beca_cdmx = crear_beca(
            db,
            institucion.id,
            "Beca CDMX Test",
        )
        beca_cdmx.ubicacion = "CDMX"

        beca_otro_lugar = crear_beca(
            db,
            institucion.id,
            "Beca EdoMex Test",
        )
        beca_otro_lugar.ubicacion = "Estado de México"

        db.commit()

        service = BecaService(db)

        filtros = BecaFiltros(
            ubicacion="CDMX",
        )

        items, total = service.buscar_becas(
            filtros,
            skip=0,
            limit=20,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].nombre == "Beca CDMX Test"
        assert items[0].ubicacion == "CDMX"

        assert beca_otro_lugar.ubicacion == "Estado de México"

    finally:
        db.close()
        engine.dispose()


def test_buscar_becas_por_texto() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        beca = crear_beca(
            db,
            institucion.id,
            "Beca Ingeniería de Sistemas",
        )

        beca.requisitos = (
            "Estudiar una carrera relacionada con ingeniería."
        )

        crear_beca(
            db,
            institucion.id,
            "Beca Artes Test",
        )

        db.commit()

        service = BecaService(db)

        filtros = BecaFiltros(
            q="ingeniería",
        )

        items, total = service.buscar_becas(
            filtros,
            skip=0,
            limit=20,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].nombre == "Beca Ingeniería de Sistemas"

    finally:
        db.close()
        engine.dispose()


def test_buscar_becas_solo_devuelve_abiertas_por_defecto() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        beca_abierta = crear_beca(
            db,
            institucion.id,
            "Beca Abierta Test",
            estado=EstadoBeca.abierta,
        )

        beca_cerrada = crear_beca(
            db,
            institucion.id,
            "Beca Cerrada Test",
            estado=EstadoBeca.cerrada,
        )

        db.commit()

        service = BecaService(db)

        filtros = BecaFiltros()

        items, total = service.buscar_becas(
            filtros,
            skip=0,
            limit=20,
        )

        assert total == 1
        assert len(items) == 1
        assert items[0].id == beca_abierta.id
        assert items[0].nombre == "Beca Abierta Test"
        assert beca_cerrada.estado == EstadoBeca.cerrada

    finally:
        db.close()
        engine.dispose()


def test_buscar_becas_respeta_paginacion() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        for indice in range(5):
            crear_beca(
                db,
                institucion.id,
                f"Beca Paginada {indice}",
            )

        db.commit()

        service = BecaService(db)

        filtros = BecaFiltros()

        items, total = service.buscar_becas(
            filtros,
            skip=1,
            limit=2,
        )

        assert total == 5
        assert len(items) == 2

    finally:
        db.close()
        engine.dispose()


def test_obtener_beca_existente() -> None:
    engine, db = crear_db_en_memoria()

    try:
        institucion = crear_institucion(db)

        beca = crear_beca(
            db,
            institucion.id,
            "Beca Obtener Test",
        )

        db.commit()

        service = BecaService(db)

        resultado = service.obtener_beca(beca.id)

        assert resultado.id == beca.id
        assert resultado.nombre == "Beca Obtener Test"

    finally:
        db.close()
        engine.dispose()


def test_obtener_beca_inexistente() -> None:
    engine, db = crear_db_en_memoria()

    try:
        service = BecaService(db)

        try:
            service.obtener_beca(999999)
        except BecaNotFoundException:
            pass
        else:
            raise AssertionError(
                "Se esperaba BecaNotFoundException",
            )

    finally:
        db.close()
        engine.dispose()


def test_buscar_becas_sin_resultados() -> None:
    engine, db = crear_db_en_memoria()

    try:
        service = BecaService(db)

        filtros = BecaFiltros(
            q="esto-no-existe",
        )

        items, total = service.buscar_becas(
            filtros,
            skip=0,
            limit=20,
        )

        assert total == 0
        assert items == []

    finally:
        db.close()
        engine.dispose()