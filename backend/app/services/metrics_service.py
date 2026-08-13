from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.models.beca import Beca, EstadoBeca
from app.db.models.institucion import Institucion
from app.db.models.log_scraper import EstadoScraper, LogScraper


class MetricsService:
    def __init__(self, db: Session):
        self.db = db

    def resumen_general(self) -> dict:
        """
        Devuelve las métricas generales actuales del sistema.

        Incluye:
        - total de becas abiertas
        - total de instituciones
        - desglose de becas abiertas por nivel educativo
        - información de la última corrida del scraper

        Cuando todavía no existe ninguna corrida del scraper,
        `ultima_corrida_scraper` es None.
        """

        total_becas = (
            self.db.scalar(
                select(func.count(Beca.id)).where(
                    Beca.estado == EstadoBeca.abierta
                )
            )
            or 0
        )

        total_instituciones = (
            self.db.scalar(
                select(func.count(Institucion.id))
            )
            or 0
        )

        desglose_raw = self.db.execute(
            select(
                Beca.nivel_educativo,
                func.count(Beca.id),
            )
            .where(Beca.estado == EstadoBeca.abierta)
            .group_by(Beca.nivel_educativo)
        ).all()

        desglose = {
            nivel.value: count
            for nivel, count in desglose_raw
        }

        ultima_corrida = self.db.scalar(
            select(LogScraper)
            .order_by(desc(LogScraper.fecha_ejecucion))
            .limit(1)
        )

        ultima_corrida_scraper = None

        if ultima_corrida is not None:
            ultima_corrida_scraper = {
                "fecha": ultima_corrida.fecha_ejecucion,
                "estado": ultima_corrida.estado.value,
            }

        return {
            "total_becas_activas": total_becas,
            "total_instituciones": total_instituciones,
            "desglose_niveles": desglose,
            "ultima_corrida_scraper": ultima_corrida_scraper,
        }

    def historial_scraper(self, limit: int = 20) -> list[LogScraper]:
        """
        Devuelve las corridas más recientes del scraper.
        """

        if limit < 1:
            return []

        corridas = self.db.scalars(
            select(LogScraper)
            .order_by(desc(LogScraper.fecha_ejecucion))
            .limit(limit)
        ).all()

        return list(corridas)

    def tasa_exito_scraper(
        self,
        ultimas_n: int = 20,
    ) -> float | None:
        """
        Calcula el porcentaje de corridas exitosas entre las últimas N.

        Devuelve:
            - porcentaje entre 0.0 y 100.0 si existen corridas
            - None si todavía no existen corridas
        """

        if ultimas_n < 1:
            return None

        corridas = self.db.scalars(
            select(LogScraper)
            .order_by(desc(LogScraper.fecha_ejecucion))
            .limit(ultimas_n)
        ).all()

        if not corridas:
            return None

        exitosas = sum(
            1
            for corrida in corridas
            if corrida.estado == EstadoScraper.exito
        )

        return (exitosas / len(corridas)) * 100.0