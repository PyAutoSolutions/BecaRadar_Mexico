import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TipoInstitucion(str, enum.Enum):
    gobierno = "gobierno"
    universidad_publica = "universidad_publica"
    universidad_privada = "universidad_privada"
    fundacion = "fundacion"

class Institucion(Base):
    __tablename__ = "instituciones"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    tipo: Mapped[TipoInstitucion] = mapped_column(Enum(TipoInstitucion))
    sitio_web: Mapped[str | None] = mapped_column(String(500))

    becas: Mapped[list["Beca"]] = relationship(back_populates="institucion")

if TYPE_CHECKING:
    from app.db.models.beca import Beca
