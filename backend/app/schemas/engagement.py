"""Schemas de guardadas, cobertura, alertas y dispositivos (5.6-5.8)."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Flag, ORMModel


# --- Guardadas --------------------------------------------------------------
class SavedItem(BaseModel):
    id: str
    address: str
    city: str
    flag: Flag | None = None
    opening_price: int | None = None
    saved_at: datetime


class SavedList(BaseModel):
    items: list[SavedItem]


class SaveRequest(BaseModel):
    property_id: str


# --- Cobertura --------------------------------------------------------------
class CoverageItem(ORMModel):
    id: str
    type: str
    ref_id: str
    label: str | None = None


class CoverageList(BaseModel):
    items: list[CoverageItem]


class CoverageRequest(BaseModel):
    type: str = Field(..., pattern="^(county|zip)$")
    ref_id: str


# --- Alertas ----------------------------------------------------------------
class AlertItem(ORMModel):
    id: str
    type: str
    property_id: str | None = None
    title: str
    body: str | None = None
    read: bool
    created_at: datetime


class AlertList(BaseModel):
    items: list[AlertItem]
    unread_count: int


class UpdateAlertRequest(BaseModel):
    read: bool


class AlertChannels(BaseModel):
    push: bool = True
    email: bool = False
    sms: bool = False


class AlertSettings(BaseModel):
    new_property: bool = True
    price_drop: bool = True
    auction_reminder: bool = True
    channels: AlertChannels = AlertChannels()


class UpdateAlertSettings(BaseModel):
    new_property: bool | None = None
    price_drop: bool | None = None
    auction_reminder: bool | None = None
    channels: dict | None = None


# --- Dispositivos -----------------------------------------------------------
class DeviceRequest(BaseModel):
    token: str
    platform: str = Field(..., pattern="^(ios|android)$")
