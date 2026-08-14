import hashlib
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import BecaNotFoundException
from app.db.models.beca import Beca, EstadoBeca
from app.db.models.institucion import Institucion
from app.schemas.beca import BecaCreate, BecaFiltros, BecaUpdate


class BecaService:
    def __init__(self, db: Session):
        self.db = db

    def buscar_becas(
        self,
        filtros: BecaFiltros,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Beca], int]:
        query = select(Beca).options(
            joinedload(Beca.institucion)
        )

        count_query = select(
            func.count(Beca.id)
        )

        # ---------------------------------------------------------
        # Estado
        # ---------------------------------------------------------
        estado = filtros.estado

        if estado is None:
            estado = EstadoBeca.abierta

        query = query.where(
            Beca.estado == estado
        )

        count_query = count_query.where(
            Beca.estado == estado
        )

        # ---------------------------------------------------------
        # Nivel educativo
        # ---------------------------------------------------------
        if filtros.nivel_educativo is not None:
            query = query.where(
                Beca.nivel_educativo
                == filtros.nivel_educativo
            )

            count_query = count_query.where(
                Beca.nivel_educativo
                == filtros.nivel_educativo
            )

        # ---------------------------------------------------------
        # InstituciÃ³n
        # ---------------------------------------------------------
        if filtros.institucion_id is not None:
            query = query.where(
                Beca.institucion_id
                == filtros.institucion_id
            )

            count_query = count_query.where(
                Beca.institucion_id
                == filtros.institucion_id
            )

        # ---------------------------------------------------------
        # Cobertura 100%
        # ---------------------------------------------------------
        if filtros.cobertura_100:
            cobertura_filter = Beca.cobertura.ilike(
                "%100%"
            )

            query = query.where(
                cobertura_filter
            )

            count_query = count_query.where(
                cobertura_filter
            )

        # ---------------------------------------------------------
        # UbicaciÃ³n
        # ---------------------------------------------------------
        if filtros.ubicacion:
            ubicacion = filtros.ubicacion.strip()

            if ubicacion.lower() in {
                "cdmx",
                "ciudad de mexico",
                "ciudad de mÃ©xico",
            }:
                # Acepta las dos formas en que puede estar
                # almacenada la ubicaciÃ³n.
                ubicacion_filter = or_(
                    Beca.ubicacion.ilike("%CDMX%"),
                    Beca.ubicacion.ilike(
                        "%Ciudad de MÃ©xico%"
                    ),
                    Beca.ubicacion.ilike(
                        "%Ciudad de Mexico%"
                    ),
                )
            else:
                ubicacion_filter = Beca.ubicacion.ilike(
                    f"%{ubicacion}%"
                )

            query = query.where(
                ubicacion_filter
            )

            count_query = count_query.where(
                ubicacion_filter
            )

        # ---------------------------------------------------------
        # BÃºsqueda libre
        # ---------------------------------------------------------
        if filtros.q:
            texto = filtros.q.strip()

            if texto:
                patron = f"%{texto}%"

                texto_filter = or_(
                    Beca.nombre.ilike(patron),
                    Beca.requisitos.ilike(patron),
                    Beca.cobertura.ilike(patron),
                )

                query = query.where(
                    texto_filter
                )

                count_query = count_query.where(
                    texto_filter
                )

        # ---------------------------------------------------------
        # Becas nuevas
        # ---------------------------------------------------------
        if filtros.nuevas_dias is not None:
            fecha_desde = (
                datetime.now(UTC).replace(tzinfo=None)
                - timedelta(
                    days=filtros.nuevas_dias
                )
            )

            nuevas_filter = (
                Beca.created_at >= fecha_desde
            )

            query = query.where(
                nuevas_filter
            )

            count_query = count_query.where(
                nuevas_filter
            )

        # ---------------------------------------------------------
        # Conteo total
        # ---------------------------------------------------------
        total = (
            self.db.scalar(count_query)
            or 0
        )

        # ---------------------------------------------------------
        # PaginaciÃ³n
        # ---------------------------------------------------------
        items = (
            self.db.scalars(
                query
                .offset(skip)
                .limit(limit)
            )
            .unique()
            .all()
        )

        return items, total

    def obtener_beca(
        self,
        beca_id: int,
    ) -> Beca:
        beca = self.db.get(
            Beca,
            beca_id,
        )

        if beca is None:
            raise BecaNotFoundException(
                f"Beca con id {beca_id} no encontrada."
            )

        return beca

    def crear_beca(
        self,
        data: BecaCreate,
    ) -> Beca:
        institucion = self.db.scalar(
            select(Institucion).where(
                Institucion.nombre
                == data.institucion_nombre
            )
        )

        if institucion is None:
            institucion = Institucion(
                nombre=data.institucion_nombre,
                tipo="universidad_publica",
            )

            self.db.add(institucion)
            self.db.flush()

        beca = Beca(
            nombre=data.nombre,
            institucion_id=institucion.id,
            tipo=data.tipo,
            cobertura=data.cobertura,
            nivel_educativo=data.nivel_educativo,
            requisitos=data.requisitos,
            ubicacion=data.ubicacion,
            fecha_apertura=data.fecha_apertura,
            fecha_limite=data.fecha_limite,
            estado=EstadoBeca.abierta,
            link_oficial=str(data.link_oficial),
            fuente_scraper="manual",
            hash_contenido=hashlib.sha1(f"{data.nombre}|{data.fecha_limite}|{data.cobertura}|{data.requisitos}".encode("utf-8")).hexdigest(),
            ultima_verificacion=datetime.now(UTC).replace(tzinfo=None),
        )

        self.db.add(beca)

        try:
            self.db.commit()
            self.db.refresh(beca)
        except IntegrityError:
            self.db.rollback()
            raise

        return beca

    def actualizar_beca(
        self,
        beca_id: int,
        data: BecaUpdate,
    ) -> Beca:
        beca = self.obtener_beca(
            beca_id
        )

        cambios = data.model_dump(
            exclude_unset=True,
            exclude_none=True,
        )

        if "institucion_nombre" in cambios:
            nombre_institucion = cambios.pop(
                "institucion_nombre"
            )

            institucion = self.db.scalar(
                select(Institucion).where(
                    Institucion.nombre
                    == nombre_institucion
                )
            )

            if institucion is None:
                institucion = Institucion(
                    nombre=nombre_institucion,
                    tipo="universidad_publica",
                )

                self.db.add(institucion)
                self.db.flush()

            beca.institucion_id = institucion.id

        if "link_oficial" in cambios:
            cambios["link_oficial"] = str(
                cambios["link_oficial"]
            )

        for campo, valor in cambios.items():
            if hasattr(beca, campo):
                setattr(
                    beca,
                    campo,
                    valor,
                )

        beca.updated_at = datetime.now(UTC).replace(tzinfo=None)

        try:
            self.db.commit()
            self.db.refresh(beca)
        except IntegrityError:
            self.db.rollback()
            raise

        return beca

    def eliminar_beca(
        self,
        beca_id: int,
    ) -> None:
        beca = self.obtener_beca(
            beca_id
        )

        self.db.delete(beca)

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
