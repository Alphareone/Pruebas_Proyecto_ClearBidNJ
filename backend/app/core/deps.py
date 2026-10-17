"""Dependencias reutilizables: sesión de BD, usuario actual y control de roles."""
from collections.abc import Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User

# auto_error=False para poder devolver nuestro formato de error estándar.
_bearer = HTTPBearer(auto_error=False, description="Bearer <access_token>")


async def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Valida el access token y devuelve el usuario autenticado y activo."""
    if creds is None or not creds.credentials:
        raise errors.unauthorized()
    try:
        payload = decode_token(creds.credentials)
    except jwt.ExpiredSignatureError:
        raise errors.unauthorized("El token ha expirado.")
    except jwt.PyJWTError:
        raise errors.unauthorized("Token inválido.")

    if payload.get("type") != "access":
        raise errors.unauthorized("Tipo de token incorrecto.")

    user = await db.get(User, payload.get("sub"))
    if user is None or not user.is_active or user.deleted_at is not None:
        raise errors.unauthorized("Usuario inexistente o inactivo.")
    return user


def require_roles(*roles: str) -> Callable:
    """Genera una dependencia que exige uno de los roles indicados."""

    async def _dep(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise errors.forbidden(
                f"Requiere rol: {', '.join(roles)}. Rol actual: {user.role}."
            )
        return user

    return _dep


# Atajos frecuentes
require_analyst = require_roles("analyst", "admin")
require_admin = require_roles("admin")
