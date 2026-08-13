"""Initial schema.

Revision ID: 001
Revises:
Create Date: 2026-08-12
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the initial database schema."""

    # ---------------------------------------------------------
    # Tabla: instituciones
    # ---------------------------------------------------------
    op.create_table(
        "instituciones",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "nombre",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "tipo",
            sa.Enum(
                "gobierno",
                "universidad_publica",
                "universidad_privada",
                "fundacion",
                name="tipoinstitucion",
            ),
            nullable=False,
        ),
        sa.Column(
            "sitio_web",
            sa.String(length=500),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nombre"),
    )

    # ---------------------------------------------------------
    # Tabla: becas
    # ---------------------------------------------------------
    op.create_table(
        "becas",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "nombre",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "institucion_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "tipo",
            sa.Enum(
                "academica",
                "deportiva",
                "cultural",
                "apoyo_economico",
                name="tipobeca",
            ),
            nullable=False,
        ),
        sa.Column(
            "cobertura",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "nivel_educativo",
            sa.Enum(
                "basica",
                "preparatoria",
                "universidad",
                "posgrado",
                "general",
                name="niveleducativo",
            ),
            nullable=False,
        ),
        sa.Column(
            "requisitos",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "ubicacion",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "fecha_apertura",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "fecha_limite",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "estado",
            sa.Enum(
                "abierta",
                "cerrada",
                "proximamente",
                name="estadobeca",
            ),
            nullable=False,
        ),
        sa.Column(
            "link_oficial",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "fuente_scraper",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "hash_contenido",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "ultima_verificacion",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["institucion_id"],
            ["instituciones.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Índices de becas.
    op.create_index(
        "ix_becas_nombre",
        "becas",
        ["nombre"],
        unique=False,
    )

    op.create_index(
        "ix_becas_estado_nivel",
        "becas",
        ["estado", "nivel_educativo"],
        unique=False,
    )

    # ---------------------------------------------------------
    # Tabla: usuarios_bot
    # ---------------------------------------------------------
    op.create_table(
        "usuarios_bot",
        sa.Column(
            "telegram_user_id",
            sa.Integer(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "first_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "alertas_activas",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "filtros_guardados",
            sa.Text(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("telegram_user_id"),
    )

    # ---------------------------------------------------------
    # Tabla: logs_scraper
    # ---------------------------------------------------------
    op.create_table(
        "logs_scraper",
        sa.Column(
            "id",
            sa.Integer(),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            "fuente",
            sa.Enum(
                "benito_juarez",
                "unam",
                "ipn",
                "tec",
                name="fuentescraper",
            ),
            nullable=False,
        ),
        sa.Column(
            "fecha_ejecucion",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "becas_encontradas",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "becas_nuevas",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "becas_actualizadas",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "errores",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "duracion_segundos",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "estado",
            sa.Enum(
                "exito",
                "error",
                "parcial",
                name="estadoscraper",
            ),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_logs_scraper_fecha_ejecucion",
        "logs_scraper",
        ["fecha_ejecucion"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial database schema."""

    # Las tablas con dependencias se eliminan primero.
    op.drop_table("logs_scraper")
    op.drop_table("usuarios_bot")

    op.drop_index(
        "ix_becas_estado_nivel",
        table_name="becas",
    )

    op.drop_index(
        "ix_becas_nombre",
        table_name="becas",
    )

    op.drop_table("becas")
    op.drop_table("instituciones")