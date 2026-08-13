from datetime import UTC, datetime

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


def crear_institucion(
    db_session,
    nombre: str,
    tipo: TipoInstitucion = TipoInstitucion.universidad_publica,
) -> Institucion:
    """Crea una institución de prueba."""
    institucion = Institucion(
        nombre=nombre,
        tipo=tipo,
        sitio_web="https://example.com/",
    )

    db_session.add(institucion)
    db_session.flush()

    return institucion


def crear_beca(
    db_session,
    institucion_id: int,
    nombre: str,
    nivel: NivelEducativo = NivelEducativo.universidad,
    estado: EstadoBeca = EstadoBeca.abierta,
    cobertura: str = "Apoyo económico",
) -> Beca:
    """Crea una beca de prueba."""
    beca = Beca(
        nombre=nombre,
        institucion_id=institucion_id,
        tipo=TipoBeca.academica,
        cobertura=cobertura,
        nivel_educativo=nivel,
        requisitos="Cumplir los requisitos.",
        ubicacion="CDMX",
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

    db_session.add(beca)
    db_session.flush()

    return beca


def crear_log_scraper(
    db_session,
    fuente: FuenteScraper,
    estado: EstadoScraper,
    becas_encontradas: int = 0,
    becas_nuevas: int = 0,
    becas_actualizadas: int = 0,
) -> LogScraper:
    """Crea una ejecución de scraper de prueba."""
    log = LogScraper(
        fuente=fuente,
        estado=estado,
        fecha_ejecucion=datetime.now(UTC).replace(tzinfo=None),
        becas_encontradas=becas_encontradas,
        becas_nuevas=becas_nuevas,
        becas_actualizadas=becas_actualizadas,
        errores=None,
        duracion_segundos=1.0,
    )

    db_session.add(log)
    db_session.flush()

    return log


def test_stats_resumen_devuelve_200(client, db_session):
    """GET /stats/resumen debe responder correctamente."""
    institucion = crear_institucion(
        db_session,
        "Institución Stats Test",
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Prepa Stats",
        nivel=NivelEducativo.preparatoria,
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Universidad Stats",
        nivel=NivelEducativo.universidad,
    )

    db_session.commit()

    response = client.get("/api/v1/stats/resumen")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "total_becas_activas" in data
    assert "total_instituciones" in data
    assert "desglose_niveles" in data
    assert "ultima_corrida_scraper" in data


def test_stats_resumen_cuenta_becas_activas(client, db_session):
    """El resumen debe contar solamente las becas abiertas."""
    institucion = crear_institucion(
        db_session,
        "Institución Activas Test",
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Abierta Stats",
        estado=EstadoBeca.abierta,
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Cerrada Stats",
        estado=EstadoBeca.cerrada,
    )

    db_session.commit()

    response = client.get("/api/v1/stats/resumen")

    assert response.status_code == 200

    data = response.json()

    assert data["total_becas_activas"] == 1


def test_stats_resumen_cuenta_instituciones(client, db_session):
    """El resumen debe contar instituciones."""
    crear_institucion(
        db_session,
        "Institución Stats 1",
    )

    crear_institucion(
        db_session,
        "Institución Stats 2",
    )

    db_session.commit()

    response = client.get("/api/v1/stats/resumen")

    assert response.status_code == 200

    data = response.json()

    assert data["total_instituciones"] == 2


def test_stats_resumen_desglose_por_nivel(client, db_session):
    """El resumen debe devolver el desglose por nivel educativo."""
    institucion = crear_institucion(
        db_session,
        "Institución Niveles Stats",
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Prepa 1",
        nivel=NivelEducativo.preparatoria,
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Prepa 2",
        nivel=NivelEducativo.preparatoria,
    )

    crear_beca(
        db_session,
        institucion.id,
        "Beca Universidad 1",
        nivel=NivelEducativo.universidad,
    )

    db_session.commit()

    response = client.get("/api/v1/stats/resumen")

    assert response.status_code == 200

    data = response.json()
    desglose = data["desglose_niveles"]

    assert desglose["preparatoria"] == 2
    assert desglose["universidad"] == 1


def test_stats_resumen_sin_scraper_devuelve_valor_nulo(client):
    """Sin corridas del scraper, no debe producir un error."""
    response = client.get("/api/v1/stats/resumen")

    assert response.status_code == 200

    data = response.json()

    assert data["total_becas_activas"] == 0
    assert data["total_instituciones"] == 0
    assert data["desglose_niveles"] == {}
    assert data["ultima_corrida_scraper"] is None


def test_stats_resumen_incluye_ultima_corrida(client, db_session):
    """El resumen debe incluir información de la última corrida."""
    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.benito_juarez,
        estado=EstadoScraper.exito,
        becas_encontradas=10,
        becas_nuevas=3,
        becas_actualizadas=2,
    )

    db_session.commit()

    response = client.get("/api/v1/stats/resumen")

    assert response.status_code == 200

    data = response.json()

    ultima = data["ultima_corrida_scraper"]

    assert ultima is not None
    assert ultima["estado"] == "exito"
    assert ultima["fecha"] is not None


def test_stats_scraper_devuelve_200(client, db_session):
    """GET /stats/scraper debe responder correctamente."""
    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.benito_juarez,
        estado=EstadoScraper.exito,
    )

    db_session.commit()

    response = client.get("/api/v1/stats/scraper")

    assert response.status_code == 200


def test_stats_scraper_devuelve_registros(client, db_session):
    """El endpoint debe devolver las corridas registradas."""
    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.benito_juarez,
        estado=EstadoScraper.exito,
        becas_encontradas=10,
        becas_nuevas=2,
    )

    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.unam,
        estado=EstadoScraper.exito,
        becas_encontradas=20,
        becas_nuevas=5,
    )

    db_session.commit()

    response = client.get("/api/v1/stats/scraper")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 2


def test_stats_scraper_responde_lista_vacia_sin_registros(client):
    """Sin corridas, el historial debe devolver una lista vacía."""
    response = client.get("/api/v1/stats/scraper")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert data == []


def test_stats_scraper_limit(client, db_session):
    """El endpoint debe respetar el límite solicitado."""
    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.benito_juarez,
        estado=EstadoScraper.exito,
    )

    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.unam,
        estado=EstadoScraper.exito,
    )

    crear_log_scraper(
        db_session,
        fuente=FuenteScraper.ipn,
        estado=EstadoScraper.parcial,
    )

    db_session.commit()

    response = client.get(
        "/api/v1/stats/scraper",
        params={"limit": 2},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2