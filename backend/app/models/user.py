"""Modelos de usuario, autenticación y 2FA."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import new_id
from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("usr"))
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)
    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    # investor | analyst | admin
    role: Mapped[str] = mapped_column(String(20), default="investor", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    preferences: Mapped["UserPreference"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"
    __table_args__ = (UniqueConstraint("provider", "provider_uid", name="uq_provider_uid"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("oau"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # google|apple|facebook
    provider_uid: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")


class RefreshToken(Base, TimestampMixin):
    __tablename__ = "refresh_tokens"

    jti: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("rft"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OtpChallenge(Base, TimestampMixin):
    """Reto 2FA por SMS. Puede existir antes de activar la cuenta."""
    __tablename__ = "otp_challenges"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("chl"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code_hash: Mapped[str] = mapped_column(String, nullable=False)
    purpose: Mapped[str] = mapped_column(String(30), default="login", nullable=False)  # login|register|phone_change
    method: Mapped[str] = mapped_column(String(10), default="sms", nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # dato temporal para cambio de teléfono
    pending_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)


class PasswordResetToken(Base, TimestampMixin):
    __tablename__ = "password_reset_tokens"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("prt"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserPreference(Base, TimestampMixin):
    __tablename__ = "user_preferences"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    language: Mapped[str] = mapped_column(String(5), default="en", nullable=False)  # en|es|zh|de
    theme: Mapped[str] = mapped_column(String(10), default="system", nullable=False)  # light|dark|system

    user: Mapped["User"] = relationship(back_populates="preferences")


class Device(Base, TimestampMixin):
    __tablename__ = "devices"
    __table_args__ = (UniqueConstraint("token", name="uq_device_token"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("dev"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    platform: Mapped[str] = mapped_column(String(10), nullable=False)  # ios|android


class AlertSetting(Base, TimestampMixin):
    __tablename__ = "alert_settings"

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    new_property: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    price_drop: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auction_reminder: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    channel_push: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    channel_email: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    channel_sms: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
