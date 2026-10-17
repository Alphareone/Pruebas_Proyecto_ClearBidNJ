"""Modelos de interacción del usuario: guardadas, cobertura, alertas, segmentos."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security import new_id
from app.db.base import Base, TimestampMixin


class SavedProperty(Base, TimestampMixin):
    __tablename__ = "saved_properties"
    __table_args__ = (UniqueConstraint("user_id", "property_id", name="uq_user_property"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("sav"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )


class CoverageArea(Base, TimestampMixin):
    __tablename__ = "coverage_areas"
    __table_args__ = (
        UniqueConstraint("user_id", "type", "ref_id", name="uq_user_coverage"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("cov"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # county|zip
    ref_id: Mapped[str] = mapped_column(String(60), nullable=False)
    label: Mapped[str | None] = mapped_column(String(160), nullable=True)


class Alert(Base, TimestampMixin):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("alt"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    # new_property | price_drop | auction_reminder
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    property_id: Mapped[str | None] = mapped_column(
        ForeignKey("properties.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)


class Segment(Base, TimestampMixin):
    """Filtro con nombre guardado por usuario (sección 6.2)."""
    __tablename__ = "segments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("seg"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    filters: Mapped[str] = mapped_column(Text, nullable=False)  # JSON serializado
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
