"""Primitivas de seguridad: hashing de contraseñas, JWT e IDs con prefijo."""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings

_ph = PasswordHasher()


# --- Contraseñas (Argon2) ---------------------------------------------------
def hash_password(plain: str) -> str:
    return _ph.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, plain)
    except VerifyMismatchError:
        return False


# --- IDs con prefijo estilo Stripe (usr_..., prp_..., etc.) -----------------
def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:20]}"


# --- JWT --------------------------------------------------------------------
def _encode(payload: dict, expires: timedelta) -> str:
    now = datetime.now(timezone.utc)
    to_encode = {**payload, "iat": now, "exp": now + expires}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: str, role: str) -> str:
    return _encode(
        {"sub": user_id, "role": role, "type": "access"},
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: str, jti: str) -> str:
    return _encode(
        {"sub": user_id, "jti": jti, "type": "refresh"},
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """Decodifica y valida firma/expiración. Lanza jwt.PyJWTError si es inválido."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


def access_expires_in() -> int:
    return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
