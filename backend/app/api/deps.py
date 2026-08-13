from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.beca_service import BecaService
from app.services.metrics_service import MetricsService


def get_beca_service(db: Session = Depends(get_db)) -> BecaService:
    return BecaService(db)

def get_metrics_service(db: Session = Depends(get_db)) -> MetricsService:
    return MetricsService(db)

class PaginationParams:
    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Registros a omitir"),
        limit: int = Query(20, ge=1, le=100, description="Límite de registros por página")
    ):
        self.skip = skip
        self.limit = limit