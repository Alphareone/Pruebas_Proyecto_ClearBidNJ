"""Schemas de geografía (sección 5.3)."""
from app.schemas.common import ORMModel


class CountyItem(ORMModel):
    id: str
    name: str
    state: str
    main_city: str | None = None
    opportunity_count: int = 0


class CountyList(ORMModel):
    items: list[CountyItem]
    total: int


class CountyDetail(ORMModel):
    id: str
    name: str
    state: str
    opportunity_count: int = 0
    by_flag: dict[str, int] = {}


class ZipItem(ORMModel):
    zip: str
    city: str
    county_id: str
    opportunity_count: int = 0


class ZipList(ORMModel):
    items: list[ZipItem]
