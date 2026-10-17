"""Módulo 5.7 — Área de cobertura."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.engagement import CoverageArea
from app.models.geography import County, ZipCode
from app.models.user import User
from app.schemas.engagement import CoverageItem, CoverageList, CoverageRequest

router = APIRouter(prefix="/coverage", tags=["Área de cobertura"])


@router.get("", response_model=CoverageList, summary="Listar zonas seguidas por el usuario")
async def list_coverage(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    rows = (
        await db.execute(
            select(CoverageArea).where(CoverageArea.user_id == user.id)
        )
    ).scalars().all()
    return CoverageList(items=[CoverageItem.model_validate(c) for c in rows])


@router.post(
    "",
    response_model=CoverageItem,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir county o ZIP al área de cobertura",
    responses={404: {}, 409: {"description": "Ya en cobertura"}, 422: {}},
)
async def add_coverage(
    body: CoverageRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Resuelve la etiqueta y valida existencia de la referencia
    if body.type == "county":
        county = await db.get(County, body.ref_id)
        if county is None:
            raise errors.not_found("County inexistente.")
        label = f"{county.name} County"
    else:  # zip
        zc = await db.get(ZipCode, body.ref_id)
        if zc is None:
            raise errors.not_found("ZIP inexistente.")
        label = f"ZIP {zc.zip}"

    exists = (
        await db.execute(
            select(CoverageArea).where(
                CoverageArea.user_id == user.id,
                CoverageArea.type == body.type,
                CoverageArea.ref_id == body.ref_id,
            )
        )
    ).scalar_one_or_none()
    if exists:
        raise errors.conflict("La zona ya está en cobertura.")

    cov = CoverageArea(user_id=user.id, type=body.type, ref_id=body.ref_id, label=label)
    db.add(cov)
    await db.flush()
    return CoverageItem.model_validate(cov)


@router.delete(
    "/{coverage_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una zona del área de cobertura",
    responses={404: {}},
)
async def remove_coverage(
    coverage_id: str, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cov = await db.get(CoverageArea, coverage_id)
    if cov is None or cov.user_id != user.id:
        raise errors.not_found("Zona de cobertura inexistente.")
    await db.delete(cov)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
