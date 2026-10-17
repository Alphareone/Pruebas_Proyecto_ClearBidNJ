"""Modelos de geografía: counties y códigos postales."""
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import new_id
from app.db.base import Base, TimestampMixin


class County(Base, TimestampMixin):
    __tablename__ = "counties"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("cty"))
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(2), default="NJ", index=True, nullable=False)
    main_city: Mapped[str | None] = mapped_column(String(120), nullable=True)

    zipcodes: Mapped[list["ZipCode"]] = relationship(back_populates="county")


class ZipCode(Base, TimestampMixin):
    __tablename__ = "zipcodes"

    zip: Mapped[str] = mapped_column(String(10), primary_key=True)
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    state: Mapped[str] = mapped_column(String(2), default="NJ", nullable=False)
    county_id: Mapped[str] = mapped_column(ForeignKey("counties.id"), index=True)

    county: Mapped["County"] = relationship(back_populates="zipcodes")
