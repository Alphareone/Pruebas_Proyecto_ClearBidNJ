"""Sección 6.2 — Segmentos (filtros guardados en el servidor)."""
import json

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.engagement import Segment
from app.models.property import Property
from app.models.user import User
from app.schemas.web import (
    CreateSegmentRequest,
    PropertyFilter,
    SegmentItem,
    SegmentList,
    SegmentMutationResponse,
    UpdateSegmentRequest,
)
from app.services import query as q

router = APIRouter(prefix="/segments", tags=["Segmentos (web)"])


async def _match_count(db: AsyncSession, filters: dict) -> int:
    f = PropertyFilter(**filters)
    stmt = q.apply_filters(
        select(func.count(func.distinct(Property.id))),
        county_id=f.county_id, flag=f.flag, auction_type=f.auction_type,
        property_type=f.property_type, min_opening=f.min_opening,
        max_opening=f.max_opening, min_roi=f.min_roi, q=f.q,
    )
    return (await db.execute(stmt)).scalar_one()


@router.get("", response_model=SegmentList, summary="Listar segmentos guardados")
async def list_segments(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    rows = (
        await db.execute(select(Segment).where(Segment.user_id == user.id))
    ).scalars().all()
    items = []
    for s in rows:
        filters = json.loads(s.filters)
        items.append(
            SegmentItem(
                id=s.id, name=s.name, filters=filters,
                alert_enabled=s.alert_enabled,
                match_count=await _match_count(db, filters),
                created_at=s.created_at,
            )
        )
    return SegmentList(items=items)


@router.post(
    "",
    response_model=SegmentMutationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un segmento a partir del filtro actual",
    responses={422: {}},
)
async def create_segment(
    body: CreateSegmentRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    filters = body.filters.model_dump(exclude_none=True)
    seg = Segment(
        user_id=user.id, name=body.name,
        filters=json.dumps(filters), alert_enabled=body.alert_enabled,
    )
    db.add(seg)
    await db.flush()
    return SegmentMutationResponse(
        id=seg.id, name=seg.name, match_count=await _match_count(db, filters)
    )


@router.patch(
    "/{segment_id}",
    response_model=SegmentMutationResponse,
    summary="Renombrar, actualizar filtro o (des)activar alertas de un segmento",
    responses={404: {}, 422: {}},
)
async def update_segment(
    segment_id: str, body: UpdateSegmentRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    seg = await db.get(Segment, segment_id)
    if seg is None or seg.user_id != user.id:
        raise errors.not_found("Segmento inexistente.")
    if body.name is not None:
        seg.name = body.name
    if body.filters is not None:
        seg.filters = json.dumps(body.filters.model_dump(exclude_none=True))
    if body.alert_enabled is not None:
        seg.alert_enabled = body.alert_enabled
    await db.flush()
    return SegmentMutationResponse(
        id=seg.id, name=seg.name, match_count=await _match_count(db, json.loads(seg.filters))
    )


@router.delete(
    "/{segment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un segmento",
    responses={404: {}},
)
async def delete_segment(
    segment_id: str, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    seg = await db.get(Segment, segment_id)
    if seg is None or seg.user_id != user.id:
        raise errors.not_found("Segmento inexistente.")
    await db.delete(seg)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
