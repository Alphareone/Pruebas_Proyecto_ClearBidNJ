"""Modelos de propiedades/oportunidades y sus bloques de detalle."""
from datetime import datetime

from sqlalchemy import (
    BigInteger, DateTime, Float, ForeignKey, Integer, Numeric, String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import new_id
from app.db.base import Base, TimestampMixin


class Property(Base, TimestampMixin):
    __tablename__ = "properties"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("prp"))
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    city: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    zip: Mapped[str] = mapped_column(String(10), index=True, nullable=False)
    county_id: Mapped[str] = mapped_column(ForeignKey("counties.id"), index=True, nullable=False)
    property_type: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    # green | yellow | red — copia denormalizada del último cálculo para filtrar rápido
    flag: Mapped[str | None] = mapped_column(String(10), index=True, nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String, nullable=True)
    photos: Mapped[list[str] | None] = mapped_column(String, nullable=True)  # JSON serializado
    archived: Mapped[bool] = mapped_column(default=False, nullable=False)

    financial: Mapped["PropertyFinancial"] = relationship(
        back_populates="property", cascade="all, delete-orphan", uselist=False
    )
    legal: Mapped["PropertyLegal"] = relationship(
        back_populates="property", cascade="all, delete-orphan", uselist=False
    )
    physical: Mapped["PropertyPhysical"] = relationship(
        back_populates="property", cascade="all, delete-orphan", uselist=False
    )
    documents: Mapped[list["PropertyDocument"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    county: Mapped["County"] = relationship()


class PropertyFinancial(Base):
    __tablename__ = "property_financials"

    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True
    )
    opening_price: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    total_liens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    arv: Mapped[int | None] = mapped_column(Integer, nullable=True)  # after-repair value
    estimated_repairs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    suggested_max_bid: Mapped[int | None] = mapped_column(Integer, nullable=True)
    potential_profit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_roi: Mapped[float | None] = mapped_column(Float, index=True, nullable=True)

    property: Mapped["Property"] = relationship(back_populates="financial")


class PropertyLegal(Base):
    __tablename__ = "property_legal"

    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True
    )
    # tax_lien | tax_deed | sheriff_sale | bank_owned
    auction_type: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    auction_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    case_number: Mapped[str | None] = mapped_column(String(60), nullable=True)
    title_status: Mapped[str | None] = mapped_column(String(30), nullable=True)  # clean|clouded|...
    occupancy: Mapped[str | None] = mapped_column(String(30), nullable=True)  # vacant|occupied
    required_deposit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # atributos usados por el motor de reglas (p. ej. liens senior/IRS)
    surviving_irs_lien: Mapped[int | None] = mapped_column(Integer, nullable=True)
    senior_liens: Mapped[int | None] = mapped_column(Integer, nullable=True)

    property: Mapped["Property"] = relationship(back_populates="legal")


class PropertyPhysical(Base):
    __tablename__ = "property_physical"

    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True
    )
    sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lot_sqft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    beds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    baths: Mapped[int | None] = mapped_column(Integer, nullable=True)
    year_built: Mapped[int | None] = mapped_column(Integer, nullable=True)
    condition: Mapped[str | None] = mapped_column(String(30), nullable=True)
    neighborhood: Mapped[str | None] = mapped_column(String(120), nullable=True)
    school_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    flood_zone: Mapped[str | None] = mapped_column(String(10), nullable=True)  # AE|VE|X...
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    property: Mapped["Property"] = relationship(back_populates="physical")


class PropertyDocument(Base, TimestampMixin):
    __tablename__ = "property_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("doc"))
    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str | None] = mapped_column(String(40), nullable=True)  # complaint|judgment|...
    url: Mapped[str] = mapped_column(String, nullable=False)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    property: Mapped["Property"] = relationship(back_populates="documents")
