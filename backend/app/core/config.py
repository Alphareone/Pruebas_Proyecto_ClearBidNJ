"""Configuración global de la aplicación utilizando Pydantic BaseSettings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "ClearBid NJ API"
    APP_VERSION: str = "0.1.0"
    ENV: str = "dev"
    API_V1_PREFIX: str = "/api/v1"
    DEFAULT_TZ: str = "America/New_York"

    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # JWT
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # 2FA / OTP
    OTP_LENGTH: int = 6
    OTP_EXPIRE_SECONDS: int = 300
    OTP_MAX_ATTEMPTS: int = 5

    # Password Reset
    PASSWORD_RESET_EXPIRE_MINUTES: int = 15

    # Rate Limit
    AUTH_RATE_LIMIT: int = 5
    AUTH_RATE_WINDOW_SECONDS: int = 60

    # External Providers
    SMS_PROVIDER: str = "stub"
    PUSH_PROVIDER: str = "stub"
    OAUTH_PROVIDER_MODE: str = "stub"

    # SMTP Settings (para envío real de correos)
    EMAIL_PROVIDER: str = "smtp"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: str | None = None
    EMAILS_FROM_NAME: str = "ClearBid NJ Auth"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()   