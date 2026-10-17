"""Schemas de propiedades / oportunidades y semáforo (secciones 5.4 y 5.5)."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import (
    AuctionType,
    Flag,
    ORMModel,
    PropertyType,
    Severity,
)


# --- Listado (tarjetas) -----------------------------------------------------
class PropertyListItem(BaseModel):
    id: str
    address: str
    city: str
    zip: str
    county_id: str
    property_type: PropertyType | None = None
    flag: Flag | None = None
    opening_price: int | None = None
    estimated_value: int | None = None  # ARV
    estimated_roi: float | None = None
    auction_date: datetime | None = None
    thumbnail_url: str | None = None


# --- Ficha de detalle -------------------------------------------------------
class FinancialBlock(BaseModel):
    opening_price: int | None = None
    total_liens: int | None = None
    arv: int | None = None
    estimated_repairs: int | None = None
    suggested_max_bid: int | None = None
    potential_profit: int | None = None
    estimated_roi: float | None = None


class LegalBlock(BaseModel):
    auction_type: AuctionType | None = None
    auction_date: datetime | None = None
    location: str | None = None
    case_number: str | None = None
    title_status: str | None = None
    occupancy: str | None = None
    required_deposit: int | None = None
    # Atributos usados por el motor de reglas (liens que sobreviven a la subasta)
    surviving_irs_lien: int | None = None
    senior_liens: int | None = None


class PhysicalBlock(BaseModel):
    sqft: int | None = None
    lot_sqft: int | None = None
    beds: int | None = None
    baths: int | None = None
    year_built: int | None = None
    condition: str | None = None
    neighborhood: str | None = None
    school_rating: int | None = None
    flood_zone: str | None = None
    lat: float | None = None
    lng: float | None = None


class RuleResultOut(BaseModel):
    code: str
    status: str
    severity: Severity
    title: str | None = None
    message: str | None = None


class TrafficLightOut(BaseModel):
    flag: Flag
    engine_version: str
    generated_at: datetime
    rules: list[RuleResultOut] = []


class PropertyDetail(BaseModel):
    id: str
    address: str
    city: str
    zip: str
    county_id: str
    property_type: PropertyType | None = None
    flag: Flag | None = None
    photos: list[str] = []
    financial: FinancialBlock
    legal: LegalBlock
    physical: PhysicalBlock
    traffic_light: TrafficLightOut | None = None


class DocumentItem(ORMModel):
    id: str
    name: str
    type: str | None = None
    url: str
    size_bytes: int | None = None


class DocumentList(BaseModel):
    items: list[DocumentItem]


# --- Mapa (GeoJSON) ---------------------------------------------------------
class GeoFeature(BaseModel):
    type: str = "Feature"
    geometry: dict
    properties: dict


class GeoFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoFeature]
