"""Módulo 5.3 — Geografía (counties y ZIP)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.geography import County, ZipCode
from app.models.property import Property
from app.models.user import User
from app.schemas.geography import (
    CountyDetail,
    CountyItem,
    CountyList,
    ZipItem,
    ZipList,
)

router = APIRouter(tags=["Geografía"])


@router.get(
    "/counties",
    response_model=CountyList,
    summary="Listar counties con número de oportunidades activas",
)
async def list_counties(
    state: str = Query("NJ", description="Estado (por defecto NJ)."),
    q: str | None = Query(None, description="Búsqueda por nombre o ciudad."),
    has_opportunities: bool | None = Query(None, description="Filtra los que tienen datos."),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count_sq = (
        select(Property.county_id, func.count().label("cnt"))
        .where(Property.archived.is_(False))
        .group_by(Property.county_id)
        .subquery()
    )
    stmt = (
        select(County, func.coalesce(count_sq.c.cnt, 0))
        .outerjoin(count_sq, County.id == count_sq.c.county_id)
        .where(County.state == state)
    )
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            func.lower(County.name).like(like) | func.lower(County.main_city).like(like)
        )
    rows = (await db.execute(stmt.order_by(County.name))).all()
    items = [
        CountyItem(
            id=c.id, name=c.name, state=c.state,
            main_city=c.main_city, opportunity_count=cnt,
        )
        for c, cnt in rows
        if not has_opportunities or cnt > 0
    ]
    return CountyList(items=items, total=len(items))


@router.get(
    "/counties/{county_id}",
    response_model=CountyDetail,
    summary="Detalle de county con conteos por color de semáforo",
    responses={404: {}},
)
async def get_county(
    county_id: str, _: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    county = await db.get(County, county_id)
    if county is None:
        raise errors.not_found("County inexistente.")

    rows = (
        await db.execute(
            select(Property.flag, func.count())
            .where(Property.county_id == county_id, Property.archived.is_(False))
            .group_by(Property.flag)
        )
    ).all()
    by_flag = {"green": 0, "yellow": 0, "red": 0}
    total = 0
    for flag, cnt in rows:
        if flag in by_flag:
            by_flag[flag] = cnt
        total += cnt
    return CountyDetail(
        id=county.id, name=county.name, state=county.state,
        opportunity_count=total, by_flag=by_flag,
    )


@router.get(
    "/zipcodes",
    response_model=ZipList,
    summary="Búsqueda de códigos postales para el selector de zona",
)
async def search_zipcodes(
    q: str | None = Query(None, description="Prefijo de ZIP o ciudad."),
    state: str = Query("NJ"),
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count_sq = (
        select(Property.zip, func.count().label("cnt"))
        .where(Property.archived.is_(False))
        .group_by(Property.zip)
        .subquery()
    )
    stmt = (
        select(ZipCode, func.coalesce(count_sq.c.cnt, 0))
        .outerjoin(count_sq, ZipCode.zip == count_sq.c.zip)
        .where(ZipCode.state == state)
    )
    if q:
        like = f"{q.lower()}%"
        stmt = stmt.where(
            ZipCode.zip.like(f"{q}%") | func.lower(ZipCode.city).like(like)
        )
    rows = (await db.execute(stmt.limit(50))).all()
    items = [
        ZipItem(zip=z.zip, city=z.city, county_id=z.county_id, opportunity_count=cnt)
        for z, cnt in rows
    ]
    return ZipList(items=items)
