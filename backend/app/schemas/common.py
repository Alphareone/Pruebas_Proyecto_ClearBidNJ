"""Tipos y enums compartidos por los schemas."""
from enum import Enum

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base para schemas de salida que leen de objetos ORM."""
    model_config = ConfigDict(from_attributes=True)


class Flag(str, Enum):
    green = "green"
    yellow = "yellow"
    red = "red"


class AuctionType(str, Enum):
    tax_lien = "tax_lien"
    tax_deed = "tax_deed"
    sheriff_sale = "sheriff_sale"
    bank_owned = "bank_owned"


class PropertyType(str, Enum):
    single_family = "single_family"
    condo = "condo"
    multi_family = "multi_family"
    land = "land"


class Role(str, Enum):
    investor = "investor"
    analyst = "analyst"
    admin = "admin"


class Language(str, Enum):
    en = "en"
    es = "es"
    zh = "zh"
    de = "de"


class Theme(str, Enum):
    light = "light"
    dark = "dark"
    system = "system"


class Severity(str, Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


class MessageResponse(BaseModel):
    """Respuesta genérica {campo: bool} para operaciones simples."""
    model_config = ConfigDict(extra="allow")
