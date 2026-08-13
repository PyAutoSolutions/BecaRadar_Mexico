from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UsuarioBot(Base):
    __tablename__ = "usuarios_bot"

    telegram_user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str] = mapped_column(String(255))
    alertas_activas: Mapped[bool] = mapped_column(Boolean, default=False)
    filtros_guardados: Mapped[str | None] = mapped_column(Text)