import logging
import sys
from datetime import UTC, date, datetime

from app.db.models.beca import (
    Beca,
    EstadoBeca,
    NivelEducativo,
    TipoBeca,
)
from app.db.models.institucion import Institucion, TipoInstitucion
from app.db.session import SessionLocal
from sqlalchemy.orm import Session

from scraper.extractors.cleaner import calcular_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


INSTITUCIONES_INICIALES = [
    {
        "nombre": "Tecnológico de Monterrey",
        "tipo": TipoInstitucion.universidad_privada,
        "sitio_web": "https://tec.mx/",
    },
    {
        "nombre": "Gobierno Federal",
        "tipo": TipoInstitucion.gobierno,
        "sitio_web": "https://www.gob.mx/",
    },
    {
        "nombre": "UNAM",
        "tipo": TipoInstitucion.universidad_publica,
        "sitio_web": "https://www.unam.mx/",
    },
    {
        "nombre": "IPN",
        "tipo": TipoInstitucion.universidad_publica,
        "sitio_web": "https://www.ipn.mx/",
    },
    {
        "nombre": "UAM",
        "tipo": TipoInstitucion.universidad_publica,
        "sitio_web": "https://www.uam.mx/",
    },
    {
        "nombre": "Fundación Carlos Slim",
        "tipo": TipoInstitucion.fundacion,
        "sitio_web": "https://fundacioncarlosslim.org/",
    },
]


BECAS_INICIALES = [
    {
        "nombre": "Beca Líderes del Mañana",
        "institucion_nombre": "Tecnológico de Monterrey",
        "tipo": TipoBeca.academica,
        "nivel_educativo": NivelEducativo.universidad,
        "cobertura": "100% de colegiatura para carrera completa",
        "requisitos": (
            "Promedio general mínimo de 90/100, sensibilidad social, "
            "requerir apoyo 100%."
        ),
        "ubicacion": "México",
        "fecha_apertura": None,
        "fecha_limite": date(2027, 2, 28),
        "estado": EstadoBeca.abierta,
        "link_oficial": "https://lideresdelmanana.itesm.mx/",
    },
    {
        "nombre": "Beca para el Bienestar Benito Juárez de Educación Media Superior",
        "institucion_nombre": "Gobierno Federal",
        "tipo": TipoBeca.apoyo_economico,
        "nivel_educativo": NivelEducativo.preparatoria,
        "cobertura": "Apoyo económico de $920 pesos mensuales",
        "requisitos": (
            "Estar inscrito en escuela pública de nivel bachillerato "
            "o profesional técnico."
        ),
        "ubicacion": "México",
        "fecha_apertura": None,
        "fecha_limite": None,
        "estado": EstadoBeca.abierta,
        "link_oficial": "https://www.gob.mx/becasbenitojuarez",
    },
    {
        "nombre": "Beca Manutención UNAM",
        "institucion_nombre": "UNAM",
        "tipo": TipoBeca.apoyo_economico,
        "nivel_educativo": NivelEducativo.universidad,
        "cobertura": "Apoyo económico único o semestral variable",
        "requisitos": (
            "Ser alumno regular de licenciatura en la UNAM, "
            "provenir de hogar con ingreso menor a 4 salarios mínimos."
        ),
        "ubicacion": "Ciudad de México",
        "fecha_apertura": None,
        "fecha_limite": date(2026, 10, 15),
        "estado": EstadoBeca.abierta,
        "link_oficial": "https://www.becarios.unam.mx",
    },
    {
        "nombre": "Beca Institucional IPN",
        "institucion_nombre": "IPN",
        "tipo": TipoBeca.apoyo_economico,
        "nivel_educativo": NivelEducativo.universidad,
        "cobertura": "Apoyo económico mensual según promedio",
        "requisitos": (
            "Estar inscrito en el IPN en nivel superior, "
            "promedio mínimo de 6.0 (regular)."
        ),
        "ubicacion": "Ciudad de México",
        "fecha_apertura": None,
        "fecha_limite": date(2026, 9, 30),
        "estado": EstadoBeca.abierta,
        "link_oficial": "https://www.ipn.mx/dae/servicios/becas.html",
    },
]


def seed_instituciones(db: Session) -> dict[str, int]:
    inst_map: dict[str, int] = {}

    for inst_data in INSTITUCIONES_INICIALES:
        inst = (
            db.query(Institucion)
            .filter(Institucion.nombre == inst_data["nombre"])
            .first()
        )

        if not inst:
            inst = Institucion(
                nombre=inst_data["nombre"],
                tipo=inst_data["tipo"],
                sitio_web=inst_data["sitio_web"],
            )
            db.add(inst)
            db.flush()

            logger.info("Creada institución inicial: %s", inst.nombre)
        else:
            inst.tipo = inst_data["tipo"]
            inst.sitio_web = inst_data["sitio_web"]

        inst_map[inst.nombre] = inst.id

    return inst_map


def seed_becas_iniciales(
    db: Session,
    inst_map: dict[str, int],
) -> None:
    for original_beca_data in BECAS_INICIALES:
        beca_data = original_beca_data.copy()

        inst_nombre = beca_data.pop("institucion_nombre")
        inst_id = inst_map.get(inst_nombre)

        if not inst_id:
            logger.warning(
                "Institución %s no encontrada en mapa, omitiendo.",
                inst_nombre,
            )
            continue

        beca_existente = (
            db.query(Beca)
            .filter(
                Beca.nombre == beca_data["nombre"],
                Beca.institucion_id == inst_id,
            )
            .first()
        )

        if beca_existente:
            logger.info(
                "La beca ya existe: %s",
                beca_existente.nombre,
            )
            continue

        hash_val = calcular_hash(
            {
                "nombre": beca_data["nombre"],
                "fecha_limite": (
                    beca_data["fecha_limite"].isoformat()
                    if beca_data["fecha_limite"]
                    else None
                ),
                "cobertura": beca_data["cobertura"],
                "requisitos": beca_data["requisitos"],
            }
        )

        nueva_beca = Beca(
            **beca_data,
            institucion_id=inst_id,
            fuente_scraper="manual",
            hash_contenido=hash_val,
            ultima_verificacion=datetime.now(UTC).replace(tzinfo=None),
        )

        db.add(nueva_beca)

        logger.info(
            "Creada beca inicial: %s",
            nueva_beca.nombre,
        )


def main() -> None:
    db = SessionLocal()

    try:
        logger.info("Iniciando sembrado de datos iniciales (seed)...")

        inst_map = seed_instituciones(db)
        seed_becas_iniciales(db, inst_map)

        db.commit()

        logger.info("Sembrado de datos finalizado con éxito.")

    except Exception:
        db.rollback()
        logger.exception("Error poblando datos iniciales:")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()