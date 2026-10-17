"""Punto de entrada de la aplicación FastAPI — ClearBid NJ API.

Documentación interactiva:
  - Swagger UI : /docs
  - ReDoc      : /redoc
  - OpenAPI    : /openapi.json
"""
from fastapi import FastAPI
from celery import Celery

from app.api.v1.router import api_router
from app.api.v1.utility import router as utility_router
from app.core.config import settings
from app.core.errors import register_exception_handlers

DESCRIPTION = """
API del backend de la **App de Oportunidades de Remate — New Jersey**.

Permite a inversionistas explorar propiedades en remate por *county* o código
postal, revisar la ficha de detalle (financiera, legal y física) y consultar el
**semáforo de riesgo** (verde/amarillo/rojo) calculado por el motor de reglas.

Módulos: autenticación y 2FA · usuarios y perfil · geografía · propiedades ·
semáforo y reglas · guardadas · cobertura · alertas · administración/ingesta ·
utilidad · y capacidades de la interfaz web (segmentos, exportación, batch,
facetas).

**Autenticación:** `Authorization: Bearer <access_token>` (JWT).
"""

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=DESCRIPTION,
    openapi_tags=[
        {"name": "Autenticación y 2FA", "description": "Registro, login, OAuth, 2FA por SMS y tokens."},
        {"name": "Usuarios y perfil", "description": "Perfil, contraseña, teléfono y preferencias."},
        {"name": "Geografía", "description": "Counties y códigos postales de NJ."},
        {"name": "Propiedades", "description": "Listado, ficha de detalle, mapa, facetas y semáforo (lectura)."},
        {"name": "Guardadas", "description": "Favoritos del usuario (incluye operaciones en lote)."},
        {"name": "Área de cobertura", "description": "Zonas seguidas (county/ZIP)."},
        {"name": "Alertas y notificaciones", "description": "Alertas, preferencias y dispositivos push."},
        {"name": "Segmentos (web)", "description": "Filtros guardados en el servidor."},
        {"name": "Exportación (web)", "description": "Exportación asíncrona CSV/Excel."},
        {"name": "Administración e ingesta", "description": "Reglas del motor, alta/edición de propiedades e ingesta (roles elevados)."},
        {"name": "Utilidad", "description": "Health check."},
    ],
)

# === TRABAJADOR EN SEGUNDO PLANO (CELERY) ===
celery_app = Celery(
    "clearbid_worker",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

register_exception_handlers(app)

# /health vive fuera del prefijo de versión (sección 5.10)
app.include_router(utility_router)
# Resto de endpoints bajo /api/v1
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/", include_in_schema=False)
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}