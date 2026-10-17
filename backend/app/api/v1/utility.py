"""Sección 5.10 — Utilidad (health check)."""
from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

router = APIRouter(tags=["Utilidad"])


@router.get("/health", summary="Sonda de salud", responses={503: {"description": "DB caída"}})
async def health():
    db_status = "up"
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "down"
    return {"status": "ok", "version": settings.APP_VERSION, "db": db_status}
