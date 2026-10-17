"""Agrega todos los routers del API v1."""
from fastapi import APIRouter

from app.api.v1 import (
    admin,
    alerts,
    auth,
    coverage,
    exports,
    geography,
    properties,
    saved,
    segments,
    users,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(geography.router)
api_router.include_router(properties.router)
api_router.include_router(saved.router)
api_router.include_router(coverage.router)
api_router.include_router(alerts.router)
api_router.include_router(segments.router)
api_router.include_router(exports.router)
api_router.include_router(admin.router)
