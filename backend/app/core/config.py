"""Configuración central de la aplicación.

Todos los valores se leen de variables de entorno (o de un archivo `.env`).
Ver `.env.example` para la lista completa y sus valores por defecto.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    APP_NAME: str = "ClearBid NJ API"
    APP_VERSION: str = "1.1.0"
    ENV: Literal["dev", "staging", "prod", "test"] = "dev"
    API_V1_PREFIX: str = "/api/v1"
    DEFAULT_TZ: str = "America/New_York"

    # --- Base de datos ---
    # Formato async: postgresql+asyncpg://user:pass@host:5432/db
    DATABASE_URL: str = (
        "postgresql+asyncpg://clearbid:clearbid@localhost:5432/clearbid_nj"
    )
    DB_ECHO: bool = False

    # --- JWT ---
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15   # access token de corta duración
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30     # refresh token con rotación

    # --- 2FA / OTP ---
    OTP_LENGTH: int = 6
    OTP_EXPIRE_SECONDS: int = 300           # 5 minutos
    OTP_MAX_ATTEMPTS: int = 5

    # --- Restablecimiento de contraseña ---
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30

    # --- Rate limiting (auth/2FA) ---
    AUTH_RATE_LIMIT: int = 5                # peticiones
    AUTH_RATE_WINDOW_SECONDS: int = 60      # por ventana

    # --- Paginación ---
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # --- Proveedores externos (stub | real) ---
    SMS_PROVIDER: Literal["stub", "twilio"] = "stub"
    PUSH_PROVIDER: Literal["stub", "fcm"] = "stub"
    OAUTH_PROVIDER_MODE: Literal["stub", "real"] = "stub"

    # Credenciales (solo se usan si el provider != stub)
    TWILIO_ACCOUNT_SID: str | None = None
    TWILIO_AUTH_TOKEN: str | None = None
    TWILIO_FROM_NUMBER: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    APPLE_CLIENT_ID: str | None = None
    FACEBOOK_APP_ID: str | None = None

    # --- Exportaciones ---
    EXPORT_URL_BASE: str = "https://files.clearbid-nj.com/exports"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
