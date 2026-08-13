from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from app.db.models.beca import EstadoBeca, NivelEducativo, TipoBeca
from app.db.models.institucion import TipoInstitucion


class InstitucionRead(BaseModel):
    id: int
    nombre: str
    tipo: TipoInstitucion
    sitio_web: HttpUrl | None = None
    model_config = ConfigDict(from_attributes=True)

class BecaBase(BaseModel):
    nombre: str
    tipo: TipoBeca
    cobertura: str
    nivel_educativo: NivelEducativo
    requisitos: str
    ubicacion: str | None = None
    fecha_apertura: date | None = None
    fecha_limite: date | None = None
    link_oficial: HttpUrl

class BecaCreate(BecaBase):
    institucion_nombre: str
    fuente_scraper: str = "manual"
    hash_contenido: str = "carga_manual"

class BecaUpdate(BaseModel):
    nombre: str | None = None
    tipo: TipoBeca | None = None
    cobertura: str | None = None
    nivel_educativo: NivelEducativo | None = None
    requisitos: str | None = None
    ubicacion: str | None = None
    fecha_apertura: date | None = None
    fecha_limite: date | None = None
    link_oficial: HttpUrl | None = None
    estado: EstadoBeca | None = None

class BecaRead(BecaBase):
    id: int
    institucion: InstitucionRead
    estado: EstadoBeca
    ultima_verificacion: datetime
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BecaFiltros(BaseModel):
    nivel_educativo: NivelEducativo | None = None
    cobertura_100: bool = False
    estado: EstadoBeca | None = EstadoBeca.abierta
    institucion_id: int | None = None
    ubicacion: str | None = None
    q: str | None = None
    nuevas_dias: int | None = None