from fastapi import APIRouter, Depends

from app.api.deps import PaginationParams, get_beca_service
from app.core.security import verify_api_key
from app.db.models.beca import EstadoBeca, NivelEducativo
from app.schemas.beca import BecaCreate, BecaFiltros, BecaRead, BecaUpdate
from app.schemas.common import PaginatedResponse
from app.services.beca_service import BecaService

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[BecaRead])
def listar_becas(
    nivel_educativo: NivelEducativo | None = None,
    cobertura_100: bool = False,
    estado: EstadoBeca | None = EstadoBeca.abierta,
    institucion_id: int | None = None,
    ubicacion: str | None = None,
    q: str | None = None,
    nuevas_dias: int | None = None,
    pagination: PaginationParams = Depends(),
    service: BecaService = Depends(get_beca_service)
):
    filtros = BecaFiltros(
        nivel_educativo=nivel_educativo,
        cobertura_100=cobertura_100,
        estado=estado,
        institucion_id=institucion_id,
        ubicacion=ubicacion,
        q=q,
        nuevas_dias=nuevas_dias
    )
    items, total = service.buscar_becas(filtros, skip=pagination.skip, limit=pagination.limit)
    return PaginatedResponse(items=items, total=total, skip=pagination.skip, limit=pagination.limit)

@router.get("/{beca_id}", response_model=BecaRead)
def obtener_beca(beca_id: int, service: BecaService = Depends(get_beca_service)):
    return service.obtener_beca(beca_id)

@router.post("/", response_model=BecaRead, dependencies=[Depends(verify_api_key)])
def crear_beca(data: BecaCreate, service: BecaService = Depends(get_beca_service)):
    return service.crear_beca(data)

@router.patch("/{beca_id}", response_model=BecaRead, dependencies=[Depends(verify_api_key)])
def actualizar_beca(beca_id: int, data: BecaUpdate, service: BecaService = Depends(get_beca_service)):
    return service.actualizar_beca(beca_id, data)

@router.delete("/{beca_id}", dependencies=[Depends(verify_api_key)])
def eliminar_beca(beca_id: int, service: BecaService = Depends(get_beca_service)):
    service.eliminar_beca(beca_id)
    return {"detail": "Beca eliminada correctamente"}