import secrets

from fastapi import Header

from app.core.config import settings
from app.core.exceptions import UnauthorizedException


def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if not secrets.compare_digest(x_api_key, settings.SECRET_API_KEY):
        raise UnauthorizedException(detail="Credenciales inválidas")
    return x_api_key