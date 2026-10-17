"""Módulo 5.6 — Guardadas (favoritos) + batch (sección 6.4)."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.property import Property, PropertyFinancial
from app.models.engagement import SavedProperty
from app.models.user import User
from app.schemas.engagement import SavedItem, SavedList, SaveRequest
from app.schemas.web import SavedBatchRequest, SavedBatchResponse
from app.services import query as q

router = APIRouter(prefix="/saved", tags=["Guardadas"])


@router.get("", response_model=SavedList, summary="Listar propiedades guardadas")
async def list_saved(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    rows = (
        await db.execute(
            select(SavedProperty, Property, PropertyFinancial.opening_price)
            .join(Property, Property.id == SavedProperty.property_id)
            .outerjoin(PropertyFinancial, PropertyFinancial.property_id == Property.id)
            .where(SavedProperty.user_id == user.id)
            .order_by(SavedProperty.created_at.desc())
        )
    ).all()
    items = [
        SavedItem(
            id=p.id, address=p.address, city=p.city, flag=p.flag,
            opening_price=opening, saved_at=sp.created_at,
        )
        for sp, p, opening in rows
    ]
    return SavedList(items=items)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Guardar una propiedad en favoritos",
    responses={404: {"description": "Propiedad inexistente"}, 409: {"description": "Ya guardada"}},
)
async def save_property(
    body: SaveRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if await db.get(Property, body.property_id) is None:
        raise errors.not_found("Propiedad inexistente.")
    exists = (
        await db.execute(
            select(SavedProperty).where(
                SavedProperty.user_id == user.id,
                SavedProperty.property_id == body.property_id,
            )
        )
    ).scalar_one_or_none()
    if exists:
        raise errors.conflict("La propiedad ya está guardada.")
    db.add(SavedProperty(user_id=user.id, property_id=body.property_id))
    return {"property_id": body.property_id, "saved": True}


@router.post(
    "/batch",
    response_model=SavedBatchResponse,
    summary="Agregar o quitar favoritos en lote (por IDs o filtro)",
    responses={422: {}},
)
async def saved_batch(
    body: SavedBatchRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Resuelve el conjunto de property_ids objetivo
    if body.property_ids:
        target_ids = set(body.property_ids)
    elif body.filters:
        f = body.filters
        stmt = q.apply_filters(
            select(Property.id),
            county_id=f.county_id, flag=f.flag, auction_type=f.auction_type,
            property_type=f.property_type, min_opening=f.min_opening,
            max_opening=f.max_opening, min_roi=f.min_roi, q=f.q,
        )
        target_ids = {r[0] for r in (await db.execute(stmt)).all()}
    else:
        raise errors.unprocessable("Debe enviar 'property_ids' o 'filters'.")

    existing = {
        r[0] for r in (
            await db.execute(
                select(SavedProperty.property_id).where(SavedProperty.user_id == user.id)
            )
        ).all()
    }
    added = removed = 0
    if body.action == "add":
        for pid in target_ids - existing:
            db.add(SavedProperty(user_id=user.id, property_id=pid))
            added += 1
    else:  # remove
        from sqlalchemy import delete
        to_remove = target_ids & existing
        if to_remove:
            await db.execute(
                delete(SavedProperty).where(
                    SavedProperty.user_id == user.id,
                    SavedProperty.property_id.in_(to_remove),
                )
            )
            removed = len(to_remove)
    await db.flush()
    total = (
        await db.execute(
            select(func.count()).select_from(SavedProperty).where(
                SavedProperty.user_id == user.id
            )
        )
    ).scalar_one()
    return SavedBatchResponse(added=added, removed=removed, total_saved=total)


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Quitar una propiedad de favoritos",
    responses={404: {}},
)
async def unsave_property(
    property_id: str, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sp = (
        await db.execute(
            select(SavedProperty).where(
                SavedProperty.user_id == user.id,
                SavedProperty.property_id == property_id,
            )
        )
    ).scalar_one_or_none()
    if sp is None:
        raise errors.not_found("La propiedad no está en favoritos.")
    await db.delete(sp)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
