import logging
import time
from dataclasses import dataclass
from datetime import UTC, datetime

from app.db.models.beca import Beca, EstadoBeca, TipoBeca
from app.db.models.institucion import Institucion, TipoInstitucion
from app.db.models.log_scraper import LogScraper
from app.db.session import SessionLocal
from sqlalchemy.exc import IntegrityError

from scraper.extractors.cleaner import limpiar_beca_raw
from scraper.sources.base import FuenteBase, FuenteNoDisponibleException

logger = logging.getLogger(__name__)


@dataclass
class ResultadoPipeline:
    exitoso: bool
    fuentes_procesadas: int
    fuentes_error: int


def _inferir_tipo_institucion(nombre: str) -> TipoInstitucion:
    nombre_normalizado = nombre.lower()

    if any(
        palabra in nombre_normalizado
        for palabra in (
            "gobierno",
            "secretaría",
            "secretaria",
        )
    ):
        return TipoInstitucion.gobierno

    if "fundación" in nombre_normalizado or "fundacion" in nombre_normalizado:
        return TipoInstitucion.fundacion

    if any(
        palabra in nombre_normalizado
        for palabra in (
            "unam",
            "ipn",
            "uam",
            "universidad pública",
            "universidad publica",
        )
    ):
        return TipoInstitucion.universidad_publica

    return TipoInstitucion.universidad_privada


def _inferir_tipo_beca(beca_data: dict) -> TipoBeca:
    """
    Determina el tipo de beca cuando el scraper no lo proporciona.
    """
    tipo = beca_data.pop("tipo", None)

    if isinstance(tipo, TipoBeca):
        return tipo

    if tipo is not None:
        tipo_normalizado = str(tipo).strip().lower()

        equivalencias = {
            "academica": TipoBeca.academica,
            "académica": TipoBeca.academica,
            "academic": TipoBeca.academica,
            "deportiva": TipoBeca.deportiva,
            "cultural": TipoBeca.cultural,
            "apoyo_economico": TipoBeca.apoyo_economico,
            "apoyo económico": TipoBeca.apoyo_economico,
            "economica": TipoBeca.apoyo_economico,
            "económica": TipoBeca.apoyo_economico,
            "apoyo": TipoBeca.apoyo_economico,
        }

        if tipo_normalizado in equivalencias:
            return equivalencias[tipo_normalizado]

    # Inferirlo usando el texto disponible.
    texto = " ".join(
        str(beca_data.get(campo, ""))
        for campo in (
            "nombre",
            "cobertura",
            "requisitos",
        )
    ).lower()

    if any(
        palabra in texto
        for palabra in (
            "deporte",
            "deportiva",
            "atleta",
        )
    ):
        return TipoBeca.deportiva

    if any(
        palabra in texto
        for palabra in (
            "cultura",
            "cultural",
            "artística",
            "artistica",
            "arte",
        )
    ):
        return TipoBeca.cultural

    if any(
        palabra in texto
        for palabra in (
            "apoyo económico",
            "apoyo economico",
            "dinero",
            "pesos",
            "mensual",
            "bimestral",
            "manutención",
            "manutencion",
        )
    ):
        return TipoBeca.apoyo_economico

    return TipoBeca.academica


def _normalizar_estado(beca_data: dict) -> EstadoBeca:
    estado = beca_data.pop("estado", None)

    if isinstance(estado, EstadoBeca):
        return estado

    if estado is not None:
        estado_normalizado = str(estado).strip().lower()

        equivalencias = {
            "abierta": EstadoBeca.abierta,
            "open": EstadoBeca.abierta,
            "activa": EstadoBeca.abierta,
            "true": EstadoBeca.abierta,
            "1": EstadoBeca.abierta,
            "cerrada": EstadoBeca.cerrada,
            "closed": EstadoBeca.cerrada,
            "false": EstadoBeca.cerrada,
            "0": EstadoBeca.cerrada,
            "proximamente": EstadoBeca.proximamente,
            "próximamente": EstadoBeca.proximamente,
        }

        if estado_normalizado in equivalencias:
            return equivalencias[estado_normalizado]

    activa = beca_data.pop("activa", None)

    if activa is not None:
        if isinstance(activa, bool):
            return (
                EstadoBeca.abierta
                if activa
                else EstadoBeca.cerrada
            )

        activa_normalizada = str(activa).strip().lower()

        if activa_normalizada in {
            "true",
            "1",
            "si",
            "sí",
            "abierta",
            "activa",
        }:
            return EstadoBeca.abierta

        if activa_normalizada in {
            "false",
            "0",
            "no",
            "cerrada",
        }:
            return EstadoBeca.cerrada

    return EstadoBeca.abierta


def ejecutar_pipeline(
    fuentes: list[FuenteBase],
) -> ResultadoPipeline:
    fuentes_procesadas = 0
    fuentes_error = 0

    db = SessionLocal()

    try:
        for fuente in fuentes:
            logger.info(
                "--- Iniciando procesamiento para fuente: %s ---",
                fuente.nombre,
            )

            t_inicio = time.perf_counter()

            estado_log = "exito"
            error_msg = None
            becas_nuevas = 0
            becas_actualizadas = 0

            try:
                raw_list = fuente.ejecutar()

                for raw in raw_list:
                    beca_data = limpiar_beca_raw(raw)

                    if not beca_data:
                        continue

                    # Campos heredados de scrapers anteriores
                    # que no existen en el modelo actual.
                    beca_data.pop("cobertura_100", None)

                    institucion_nombre = beca_data.pop(
                        "institucion_nombre",
                        None,
                    )

                    if not institucion_nombre:
                        logger.warning(
                            "Beca descartada porque no tiene institución."
                        )
                        continue

                    tipo_beca = _inferir_tipo_beca(beca_data)
                    estado_beca = _normalizar_estado(beca_data)

                    # El modelo Beca requiere última verificación.
                    ultima_verificacion = beca_data.pop(
                        "ultima_verificacion",
                        None,
                    )

                    if ultima_verificacion is None:
                        ultima_verificacion = datetime.now(UTC).replace(tzinfo=None)

                    # Resolver institución.
                    institucion = (
                        db.query(Institucion)
                        .filter(
                            Institucion.nombre == institucion_nombre
                        )
                        .first()
                    )

                    if not institucion:
                        institucion = Institucion(
                            nombre=institucion_nombre,
                            tipo=_inferir_tipo_institucion(
                                institucion_nombre
                            ),
                            sitio_web=None,
                        )

                        db.add(institucion)
                        db.flush()

                        logger.info(
                            "Creada institución detectada por scraper: %s",
                            institucion_nombre,
                        )

                    # Buscar beca existente.
                    beca_existente = (
                        db.query(Beca)
                        .filter(
                            Beca.nombre == beca_data["nombre"],
                            Beca.institucion_id == institucion.id,
                        )
                        .first()
                    )

                    if not beca_existente:
                        nueva_beca = Beca(
                            **beca_data,
                            institucion_id=institucion.id,
                            tipo=tipo_beca,
                            estado=estado_beca,
                            fuente_scraper=fuente.nombre,
                            ultima_verificacion=ultima_verificacion,
                        )

                        db.add(nueva_beca)
                        becas_nuevas += 1

                    else:
                        nuevo_hash = beca_data.get("hash_contenido")

                        if (
                            beca_existente.hash_contenido
                            != nuevo_hash
                        ):
                            for key, value in beca_data.items():
                                setattr(
                                    beca_existente,
                                    key,
                                    value,
                                )

                            beca_existente.tipo = tipo_beca
                            beca_existente.estado = estado_beca
                            beca_existente.fuente_scraper = fuente.nombre
                            beca_existente.ultima_verificacion = (
                                ultima_verificacion
                            )

                            becas_actualizadas += 1
                        else:
                            beca_existente.tipo = tipo_beca
                            beca_existente.estado = estado_beca
                            beca_existente.fuente_scraper = fuente.nombre
                            beca_existente.ultima_verificacion = (
                                ultima_verificacion
                            )

                db.commit()
                fuentes_procesadas += 1

                logger.info(
                    "Fuente %s procesada correctamente: "
                    "%s nuevas, %s actualizadas.",
                    fuente.nombre,
                    becas_nuevas,
                    becas_actualizadas,
                )

            except FuenteNoDisponibleException as exc:
                db.rollback()

                estado_log = "error"
                error_msg = str(exc)
                fuentes_error += 1

                logger.error(
                    "Fallo en fuente %s: %s",
                    fuente.nombre,
                    exc,
                )

            except IntegrityError as exc:
                db.rollback()

                estado_log = "error"
                error_msg = "Error de integridad en BD."
                fuentes_error += 1

                logger.error(
                    "Error de integridad en BD procesando %s: %s",
                    fuente.nombre,
                    exc,
                )

            except Exception as exc:
                db.rollback()

                estado_log = "error"
                error_msg = str(exc)
                fuentes_error += 1

                logger.exception(
                    "Error no previsto procesando %s",
                    fuente.nombre,
                )

            finally:
                duracion = int(time.perf_counter() - t_inicio)

                log_entry = LogScraper(
                    fuente=fuente.nombre,
                    estado=estado_log,
                    becas_nuevas=becas_nuevas,
                    becas_actualizadas=becas_actualizadas,
                    errores=error_msg,
                    duracion_segundos=duracion,
                )

                try:
                    db.add(log_entry)
                    db.commit()
                except Exception as exc:  # noqa: BLE001
                    db.rollback()

                    logger.error(
                        "No se pudo guardar el LogScraper para %s: %s",
                        fuente.nombre,
                        exc,
                    )

    finally:
        db.close()

    return ResultadoPipeline(
        exitoso=(fuentes_error == 0),
        fuentes_procesadas=fuentes_procesadas,
        fuentes_error=fuentes_error,
    )