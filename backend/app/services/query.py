"""Construcción del query de propiedades a partir del objeto de filtro compartido.

Reutilizado por GET /properties, /properties/facets, exportación, batch y
segmentos (secciones 5.4 y 6).
"""
from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import selectinload

from app.models.property import Property, PropertyFinancial, PropertyLegal


def apply_filters(
    stmt: Select,
    *,
    county_id: list[str] | None = None,
    zip: str | None = None,
    flag: list[str] | None = None,
    auction_type: list[str] | None = None,
    property_type: list[str] | None = None,
    min_opening: int | None = None,
    max_opening: int | None = None,
    min_roi: float | None = None,
    auction_from=None,
    auction_to=None,
    q: str | None = None,
    needs_financial: bool = False,
    needs_legal: bool = False,
) -> Select:
    """Aplica los filtros compartidos a un SELECT sobre Property."""
    stmt = stmt.where(Property.archived.is_(False))

    if county_id:
        stmt = stmt.where(Property.county_id.in_(county_id))
    if zip:
        stmt = stmt.where(Property.zip == zip)
    if flag:
        stmt = stmt.where(Property.flag.in_(flag))
    if property_type:
        stmt = stmt.where(Property.property_type.in_(property_type))
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(func.lower(Property.address).like(like), func.lower(Property.city).like(like))
        )

    join_fin = needs_financial or min_opening is not None or max_opening is not None or min_roi is not None
    join_legal = needs_legal or bool(auction_type) or auction_from is not None or auction_to is not None

    if join_fin:
        stmt = stmt.join(PropertyFinancial, PropertyFinancial.property_id == Property.id)
        if min_opening is not None:
            stmt = stmt.where(PropertyFinancial.opening_price >= min_opening)
        if max_opening is not None:
            stmt = stmt.where(PropertyFinancial.opening_price <= max_opening)
        if min_roi is not None:
            stmt = stmt.where(PropertyFinancial.estimated_roi >= min_roi)
    if join_legal:
        stmt = stmt.join(PropertyLegal, PropertyLegal.property_id == Property.id)
        if auction_type:
            stmt = stmt.where(PropertyLegal.auction_type.in_(auction_type))
        if auction_from is not None:
            stmt = stmt.where(PropertyLegal.auction_date >= auction_from)
        if auction_to is not None:
            stmt = stmt.where(PropertyLegal.auction_date <= auction_to)
    return stmt


def apply_sort(stmt: Select, sort: str | None, joined_financial: bool) -> Select:
    """Aplica ordenamiento. Requiere que PropertyFinancial/Legal estén unidos si aplica."""
    if sort == "opening_asc":
        return stmt.order_by(PropertyFinancial.opening_price.asc())
    if sort == "opening_desc":
        return stmt.order_by(PropertyFinancial.opening_price.desc())
    if sort == "roi_desc":
        return stmt.order_by(PropertyFinancial.estimated_roi.desc().nullslast())
    if sort == "auction_date":
        return stmt.order_by(PropertyLegal.auction_date.asc().nullslast())
    return stmt.order_by(Property.created_at.desc())
