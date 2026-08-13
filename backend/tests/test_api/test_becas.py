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
from sqlalchemy.orm import Session


def crear_institucion(
    db: Session,
    nombre: str,
    tipo: TipoInstitucion = TipoInstitucion.universidad_publica,
) -> Institucion:
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
    ubicacion: str | None = None,
    estado: EstadoBeca = EstadoBeca.abierta,
    requisitos: str = "Cumplir requisitos de la convocatoria.",
) -> Beca:
    beca = Beca(
        nombre=nombre,
        institucion_id=institucion_id,
        tipo=TipoBeca.academica,
        cobertura=cobertura,
        nivel_educativo=nivel,
        requisitos=requisitos,
        ubicacion=ubicacion,
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


def preparar_datos(db: Session) -> None:
    """
    Crea datos de prueba para los endpoints.
    """

    unam = crear_institucion(
        db,
        "UNAM Test API",
        TipoInstitucion.universidad_publica,
    )

    tec = crear_institucion(
        db,
        "Tec Test API",
        TipoInstitucion.universidad_privada,
    )

    crear_beca(
        db,
        unam.id,
        "Beca Prepa API Test",
        nivel=NivelEducativo.preparatoria,
        cobertura="Apoyo económico",
        ubicacion="CDMX",
        requisitos="Ser estudiante de preparatoria.",
    )

    crear_beca(
        db,
        unam.id,
        "Beca Universidad API Test",
        nivel=NivelEducativo.universidad,
        cobertura="Apoyo económico",
        ubicacion="CDMX",
        requisitos="Ser estudiante universitario.",
    )

    crear_beca(
        db,
        tec.id,
        "Beca Completa API Test",
        nivel=NivelEducativo.universidad,
        cobertura="100% de colegiatura",
        ubicacion="CDMX",
        requisitos="Cumplir los requisitos.",
    )

    crear_beca(
        db,
        tec.id,
        "Beca Artes API Test",
        nivel=NivelEducativo.universidad,
        cobertura="50% de colegiatura",
        ubicacion="Estado de México",
        requisitos="Experiencia artística.",
    )

    db.commit()


def test_listar_becas_devuelve_200(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={"limit": 5},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data

    assert isinstance(data["items"], list)
    assert isinstance(data["total"], int)


def test_listar_becas_respeta_limit(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={"limit": 2},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) <= 2
    assert data["limit"] == 2


def test_listar_becas_limit_cero_devuelve_422(client):
    response = client.get(
        "/api/v1/becas/",
        params={"limit": 0},
    )

    assert response.status_code == 422


def test_listar_becas_limit_mayor_100_devuelve_422(client):
    response = client.get(
        "/api/v1/becas/",
        params={"limit": 101},
    )

    assert response.status_code == 422


def test_listar_becas_skip_negativo_devuelve_422(client):
    response = client.get(
        "/api/v1/becas/",
        params={"skip": -1},
    )

    assert response.status_code == 422


def test_filtrar_por_preparatoria(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={
            "nivel_educativo": "preparatoria",
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["nivel_educativo"] == "preparatoria"


def test_filtrar_por_universidad(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={
            "nivel_educativo": "universidad",
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3

    for beca in data["items"]:
        assert beca["nivel_educativo"] == "universidad"


def test_filtrar_por_cobertura_100(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={
            "cobertura_100": True,
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert "100" in data["items"][0]["cobertura"]


def test_filtrar_por_ubicacion(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={
            "ubicacion": "CDMX",
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3

    for beca in data["items"]:
        assert "CDMX" in beca["ubicacion"]


def test_busqueda_por_texto(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={
            "q": "preparatoria",
            "limit": 20,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert "Prepa" in data["items"][0]["nombre"]


def test_obtener_beca_inexistente_devuelve_404(client):
    response = client.get(
        "/api/v1/becas/999999999",
    )

    assert response.status_code == 404


def test_respuesta_tiene_estructura_esperada(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={"limit": 1},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["items"]

    beca = data["items"][0]

    campos_obligatorios = {
        "id",
        "nombre",
        "tipo",
        "cobertura",
        "nivel_educativo",
        "requisitos",
        "ubicacion",
        "fecha_apertura",
        "fecha_limite",
        "link_oficial",
        "institucion",
        "estado",
        "ultima_verificacion",
        "created_at",
        "updated_at",
    }

    assert campos_obligatorios.issubset(beca.keys())

    assert "id" in beca["institucion"]
    assert "nombre" in beca["institucion"]
    assert "tipo" in beca["institucion"]


def test_paginacion_skip_y_limit(client, db_session):
    preparar_datos(db_session)

    response = client.get(
        "/api/v1/becas/",
        params={
            "skip": 1,
            "limit": 2,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["skip"] == 1
    assert data["limit"] == 2
    assert len(data["items"]) == 2