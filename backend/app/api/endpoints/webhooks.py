from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.models.usuario_bot import UsuarioBot
from app.db.session import get_db

router = APIRouter(dependencies=[Depends(verify_api_key)])

class ScraperCompletadoPayload(BaseModel):
    fuente: str
    becas_nuevas: int

@router.post("/scraper-completado")
def scraper_completado(payload: ScraperCompletadoPayload):
    # Punto de extensión para lógica futura de alertas
    return {"detail": "Evento registrado", "alertas_pendientes": payload.becas_nuevas > 0}

class UsuarioBotPayload(BaseModel):
    telegram_user_id: int
    username: str | None = None
    first_name: str | None = None
    alertas_activas: bool | None = None
    filtros_guardados: str | None = None

@router.post("/usuario")
def upsert_usuario(payload: UsuarioBotPayload, db: Session = Depends(get_db)):
    usuario = db.get(UsuarioBot, payload.telegram_user_id)
    if usuario:
        if payload.username is not None: usuario.username = payload.username
        if payload.first_name is not None: usuario.first_name = payload.first_name
        if payload.alertas_activas is not None: usuario.alertas_activas = payload.alertas_activas
        if payload.filtros_guardados is not None: usuario.filtros_guardados = payload.filtros_guardados
    else:
        usuario = UsuarioBot(
            telegram_user_id=payload.telegram_user_id,
            username=payload.username,
            first_name=payload.first_name or "Usuario",
            alertas_activas=payload.alertas_activas or False,
            filtros_guardados=payload.filtros_guardados
        )
        db.add(usuario)
    
    db.commit()
    return {"detail": "Usuario guardado exitosamente"}

@router.get("/usuario/{telegram_user_id}")
def obtener_usuario(telegram_user_id: int, db: Session = Depends(get_db)):
    usuario = db.get(UsuarioBot, telegram_user_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario