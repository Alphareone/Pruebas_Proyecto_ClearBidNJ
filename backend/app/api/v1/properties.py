"""Módulo 5.4/5.5 — Propiedades, mapa, facetas y semáforo (lectura)."""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.core.pagination import Page, PageParams
from app.db.session import get_db
from app.models.geography import County
from app.models.property import (
    Property,
    PropertyDocument,
    PropertyFinancial,
    PropertyLegal,
)
from app.models.rules import RuleResult, TrafficLightResult
from app.models.user import User
from app.schemas.property import (
    DocumentItem,
    DocumentList,
    FinancialBlock,
    GeoFeature,
    GeoFeatureCollection,
    LegalBlock,
    PhysicalBlock,
    PropertyDetail,
    PropertyListItem,
    RuleResultOut,
    TrafficLightOut,
)
from app.schemas.web import FacetsResponse
from app.services import query as q

router = APIRouter(prefix="/properties", tags=["Propiedades"])


@router.get(
    "",
    response_model=Page[PropertyListItem],
    summary="Listar oportunidades con filtros, orden y paginación",
    responses={422: {}},
)
async def list_properties(
    county_id: str | None = Query(None),
    zip: str | None = Query(None),
    flag: list[str] | None = Query(None, description="Repetible: green|yellow|red"),
    auction_type: list[str] | None = Query(None, description="Repetible"),
    property_type: list[str] | None = Query(None, description="Repetible"),
    min_opening: int | None = Query(None),
    max_opening: int | None = Query(None),
    min_roi: float | None = Query(None, description="ROI estimado mínimo (%)."),
    auction_from: datetime | None = Query(None),
    auction_to: datetime | None = Query(None),
    q_text: str | None = Query(None, alias="q", description="Texto libre (dirección/ciudad)."),
    sort: str | None = Query(
        None, description="opening_asc|opening_desc|auction_date|roi_desc"
    ),
    page: PageParams = Depends(),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    joined_fin = sort in {"opening_asc", "opening_desc", "roi_desc"} or (
        min_opening is not None or max_opening is not None or min_roi is not None
    )
    joined_legal = sort == "auction_date" or bool(auction_type) or auction_from or auction_to

    base = q.apply_filters(
        select(Property).options(
            selectinload(Property.financial), selectinload(Property.legal)
        ),
        county_id=[county_id] if county_id else None,
        zip=zip, flag=flag, auction_type=auction_type, property_type=property_type,
        min_opening=min_opening, max_opening=max_opening, min_roi=min_roi,
        auction_from=auction_from, auction_to=auction_to, q=q_text,
        needs_financial=joined_fin, needs_legal=joined_legal,
    )
    count_stmt = q.apply_filters(
        select(func.count(distinct(Property.id))),
        county_id=[county_id] if county_id else None,
        zip=zip, flag=flag, auction_type=auction_type, property_type=property_type,
        min_opening=min_opening, max_opening=max_opening, min_roi=min_roi,
        auction_from=auction_from, auction_to=auction_to, q=q_text,
    )
    total = (await db.execute(count_stmt)).scalar_one()
    stmt = q.apply_sort(base, sort, joined_fin).offset(page.offset).limit(page.limit)
    rows = (await db.execute(stmt)).scalars().unique().all()

    items = [
        PropertyListItem(
            id=p.id, address=p.address, city=p.city, zip=p.zip, county_id=p.county_id,
            property_type=p.property_type, flag=p.flag,
            opening_price=p.financial.opening_price if p.financial else None,
            estimated_value=p.financial.arv if p.financial else None,
            estimated_roi=p.financial.estimated_roi if p.financial else None,
            auction_date=p.legal.auction_date if p.legal else None,
            thumbnail_url=p.thumbnail_url,
        )
        for p in rows
    ]
    return Page.create(items, total, page)


@router.get(
    "/facets",
    response_model=FacetsResponse,
    summary="Conteos agregados por faceta para el panel de filtros (sección 6.5)",
)
async def facets(
    county_id: str | None = Query(None),
    flag: list[str] | None = Query(None),
    auction_type: list[str] | None = Query(None),
    property_type: list[str] | None = Query(None),
    min_opening: int | None = Query(None),
    max_opening: int | None = Query(None),
    min_roi: float | None = Query(None),
    q_text: str | None = Query(None, alias="q"),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    kw = dict(
        county_id=[county_id] if county_id else None, flag=flag,
        auction_type=auction_type, property_type=property_type,
        min_opening=min_opening, max_opening=max_opening, min_roi=min_roi, q=q_text,
    )
    ids_stmt = q.apply_filters(select(Property.id), **kw)
    ids = [r[0] for r in (await db.execute(ids_stmt)).all()]
    total = len(ids)

    if not ids:
        return FacetsResponse(total=0)

    flag_rows = (
        await db.execute(
            select(Property.flag, func.count()).where(Property.id.in_(ids)).group_by(Property.flag)
        )
    ).all()
    ptype_rows = (
        await db.execute(
            select(Property.property_type, func.count())
            .where(Property.id.in_(ids)).group_by(Property.property_type)
        )
    ).all()
    county_rows = (
        await db.execute(
            select(County.id, County.name, func.count())
            .join(Property, Property.county_id == County.id)
            .where(Property.id.in_(ids)).group_by(County.id, County.name)
        )
    ).all()
    at_rows = (
        await db.execute(
            select(PropertyLegal.auction_type, func.count())
            .where(PropertyLegal.property_id.in_(ids))
            .group_by(PropertyLegal.auction_type)
        )
    ).all()
    roi_vals = [
        r[0] for r in (
            await db.execute(
                select(PropertyFinancial.estimated_roi)
                .where(PropertyFinancial.property_id.in_(ids))
            )
        ).all() if r[0] is not None
    ]
    buckets = [
        {"gte": t, "count": sum(1 for v in roi_vals if v >= t)} for t in (35, 30, 20)
    ]
    return FacetsResponse(
        total=total,
        flag={k: v for k, v in flag_rows if k},
        county=[{"county_id": cid, "name": name, "count": c} for cid, name, c in county_rows],
        auction_type={k: v for k, v in at_rows if k},
        property_type={k: v for k, v in ptype_rows if k},
        roi_buckets=buckets,
    )


@router.get(
    "/map",
    response_model=GeoFeatureCollection,
    summary="Puntos para el mapa (GeoJSON FeatureCollection)",
)
async def properties_map(
    county_id: str | None = Query(None),
    bbox: str | None = Query(None, description="minLng,minLat,maxLng,maxLat"),
    flag: list[str] | None = Query(None),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.property import PropertyPhysical

    stmt = (
        select(Property, PropertyPhysical, PropertyFinancial)
        .join(PropertyPhysical, PropertyPhysical.property_id == Property.id)
        .outerjoin(PropertyFinancial, PropertyFinancial.property_id == Property.id)
        .where(Property.archived.is_(False))
    )
    if county_id:
        stmt = stmt.where(Property.county_id == county_id)
    if flag:
        stmt = stmt.where(Property.flag.in_(flag))
    if bbox:
        try:
            min_lng, min_lat, max_lng, max_lat = map(float, bbox.split(","))
        except ValueError:
            raise errors.unprocessable("bbox debe ser 'minLng,minLat,maxLng,maxLat'.")
        stmt = stmt.where(
            PropertyPhysical.lng.between(min_lng, max_lng),
            PropertyPhysical.lat.between(min_lat, max_lat),
        )

    features = []
    for p, phys, fin in (await db.execute(stmt)).all():
        if phys.lat is None or phys.lng is None:
            continue
        features.append(
            GeoFeature(
                geometry={"type": "Point", "coordinates": [phys.lng, phys.lat]},
                properties={
                    "id": p.id, "flag": p.flag,
                    "opening_price": fin.opening_price if fin else None,
                },
            )
        )
    return GeoFeatureCollection(features=features)


async def _load_full(db: AsyncSession, property_id: str) -> Property | None:
    return (
        await db.execute(
            select(Property)
            .options(
                selectinload(Property.financial),
                selectinload(Property.legal),
                selectinload(Property.physical),
            )
            .where(Property.id == property_id, Property.archived.is_(False))
        )
    ).scalar_one_or_none()


async def _traffic_light_out(db: AsyncSession, property_id: str) -> TrafficLightOut | None:
    res = await db.get(TrafficLightResult, property_id)
    if res is None:
        return None
    rules = (
        await db.execute(
            select(RuleResult).where(RuleResult.property_id == property_id)
        )
    ).scalars().all()
    return TrafficLightOut(
        flag=res.flag, engine_version=res.engine_version, generated_at=res.generated_at,
        rules=[
            RuleResultOut(
                code=r.rule_code, status=r.status, severity=r.severity,
                title=r.title, message=r.message,
            )
            for r in rules
        ],
    )


@router.get(
    "/{property_id}",
    response_model=PropertyDetail,
    summary="Ficha de detalle completa (financiero, legal, físico y semáforo)",
    responses={404: {}},
)
async def get_property(
    property_id: str, _: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    p = await _load_full(db, property_id)
    if p is None:
        raise errors.not_found("Propiedad inexistente.")
    import json

    photos = json.loads(p.photos) if p.photos else []
    return PropertyDetail(
        id=p.id, address=p.address, city=p.city, zip=p.zip, county_id=p.county_id,
        property_type=p.property_type, flag=p.flag, photos=photos,
        financial=FinancialBlock.model_validate(p.financial, from_attributes=True)
        if p.financial else FinancialBlock(),
        legal=LegalBlock.model_validate(p.legal, from_attributes=True)
        if p.legal else LegalBlock(),
        physical=PhysicalBlock.model_validate(p.physical, from_attributes=True)
        if p.physical else PhysicalBlock(),
        traffic_light=await _traffic_light_out(db, property_id),
    )


@router.get(
    "/{property_id}/documents",
    response_model=DocumentList,
    summary="Documentos del caso asociados a la propiedad",
    responses={404: {}},
)
async def property_documents(
    property_id: str, _: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if await db.get(Property, property_id) is None:
        raise errors.not_found("Propiedad inexistente.")
    docs = (
        await db.execute(
            select(PropertyDocument).where(PropertyDocument.property_id == property_id)
        )
    ).scalars().all()
    return DocumentList(items=[DocumentItem.model_validate(d) for d in docs])


@router.get(
    "/{property_id}/traffic-light",
    response_model=TrafficLightOut,
    summary="Color y reglas evaluadas de una propiedad (pestaña Semáforo)",
    responses={404: {}},
)
async def property_traffic_light(
    property_id: str, _: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    if await db.get(Property, property_id) is None:
        raise errors.not_found("Propiedad inexistente.")
    out = await _traffic_light_out(db, property_id)
    if out is None:
        raise errors.not_found("Semáforo no calculado para esta propiedad.")
    return out
