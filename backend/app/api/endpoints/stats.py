from fastapi import APIRouter, Depends

from app.api.deps import get_metrics_service
from app.services.metrics_service import MetricsService

router = APIRouter()

@router.get("/resumen")
def resumen_general(service: MetricsService = Depends(get_metrics_service)):
    return service.resumen_general()

@router.get("/scraper")
def historial_scraper(limit: int = 20, service: MetricsService = Depends(get_metrics_service)):
    return service.historial_scraper(limit)