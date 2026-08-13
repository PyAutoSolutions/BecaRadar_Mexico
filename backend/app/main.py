from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__

# Se asume la existencia de api_router y ErrorResponse en las siguientes partes
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException
from app.schemas.common import ErrorResponse

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=__version__,
    docs_url="/docs"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    error_response = ErrorResponse(error=True, detail=exc.detail, status_code=exc.status_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception):
    error_response = ErrorResponse(
        error=True, 
        detail="Error interno del servidor.", 
        status_code=500
    )
    return JSONResponse(
        status_code=500,
        content=error_response.model_dump()
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": __version__}