import enum

from sqlalchemy import DateTime, Enum, Float, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FuenteScraper(str, enum.Enum):
    benito_juarez = "benito_juarez"
    unam = "unam"
    ipn = "ipn"
    tec = "tec"


class EstadoScraper(str, enum.Enum):
    exito = "exito"
    error = "error"
    parcial = "parcial"


class LogScraper(Base):
    __tablename__ = "logs_scraper"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    fuente: Mapped[FuenteScraper] = mapped_column(
        Enum(FuenteScraper),
    )

    fecha_ejecucion: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        index=True,
    )

    becas_encontradas: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    becas_nuevas: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    becas_actualizadas: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    errores: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    duracion_segundos: Mapped[float] = mapped_column(
        Float,
    )

    estado: Mapped[EstadoScraper] = mapped_column(
        Enum(EstadoScraper),
    )