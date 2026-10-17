"""Modelos de trabajos asíncronos: ingesta de datos y exportaciones."""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.security import new_id
from app.db.base import Base, TimestampMixin


class IngestJob(Base, TimestampMixin):
    __tablename__ = "ingest_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("job"))
    source: Mapped[str] = mapped_column(String(120), nullable=False)
    county_id: Mapped[str | None] = mapped_column(ForeignKey("counties.id"), nullable=True)
    file_url: Mapped[str | None] = mapped_column(String, nullable=True)
    # queued | processing | completed | failed
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)
    created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    failed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ExportJob(Base, TimestampMixin):
    __tablename__ = "export_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("exp"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    format: Mapped[str] = mapped_column(String(10), nullable=False)  # csv|xlsx
    status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    download_url: Mapped[str | None] = mapped_column(String, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    params: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON serializado
