import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TipoBeca(str, enum.Enum):
    academica = "academica"
    deportiva = "deportiva"
    cultural = "cultural"
    apoyo_economico = "apoyo_economico"


class NivelEducativo(str, enum.Enum):
    basica = "basica"
    preparatoria = "preparatoria"
    universidad = "universidad"
    posgrado = "posgrado"
    general = "general"


class EstadoBeca(str, enum.Enum):
    abierta = "abierta"
    cerrada = "cerrada"
    proximamente = "proximamente"


class Beca(Base):
    __tablename__ = "becas"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    nombre: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    institucion_id: Mapped[int] = mapped_column(
        ForeignKey("instituciones.id")
    )

    tipo: Mapped[TipoBeca] = mapped_column(
        Enum(TipoBeca)
    )

    cobertura: Mapped[str] = mapped_column(
        String(100)
    )

    nivel_educativo: Mapped[NivelEducativo] = mapped_column(
        Enum(NivelEducativo)
    )

    requisitos: Mapped[str] = mapped_column(
        Text
    )

    ubicacion: Mapped[str | None] = mapped_column(
        String(100)
    )

    fecha_apertura: Mapped[Date | None] = mapped_column(
        Date
    )

    fecha_limite: Mapped[Date | None] = mapped_column(
        Date
    )

    estado: Mapped[EstadoBeca] = mapped_column(
        Enum(EstadoBeca)
    )

    link_oficial: Mapped[str] = mapped_column(
        String(500)
    )

    fuente_scraper: Mapped[str] = mapped_column(
        String(100)
    )

    hash_contenido: Mapped[str] = mapped_column(
        String(255)
    )

    ultima_verificacion: Mapped[DateTime] = mapped_column(
        DateTime
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )

    institucion: Mapped["Institucion"] = relationship(
        back_populates="becas"
    )

    __table_args__ = (
        Index(
            "ix_becas_estado_nivel",
            "estado",
            "nivel_educativo",
        ),
    )

if TYPE_CHECKING:
    from app.db.models.institucion import Institucion
