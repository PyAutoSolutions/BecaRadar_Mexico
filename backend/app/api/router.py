from fastapi import APIRouter

from app.api.endpoints import becas, stats, webhooks

api_router = APIRouter()

api_router.include_router(becas.router, prefix="/becas", tags=["becas"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])