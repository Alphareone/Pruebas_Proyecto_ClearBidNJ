"""Módulos 5.5 (admin de reglas/recálculo) y 5.9 — Administración e ingesta.

Todas las rutas requieren rol elevado (analyst o admin según el caso).
"""
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import require_admin, require_analyst
from app.db.session import get_db
from app.models.jobs import IngestJob
from app.models.property import (
    Property,
    PropertyFinancial,
    PropertyLegal,
    PropertyPhysical,
)
from app.models.rules import Rule
from app.models.user import User
from app.schemas.admin import (
    CreatePropertyRequest,
    IngestJobResponse,
    IngestJobStatus,
    IngestRequest,
    PropertyMutationResponse,
    UpdatePropertyRequest,
)
from app.schemas.rules import (
    CreateRuleRequest,
    RecalculateResponse,
    RuleItem,
    RuleList,
    UpdateRuleRequest,
)
from app.services import jobs_service
from app.services.property_service import recalculate_traffic_light

router = APIRouter(prefix="/admin", tags=["Administración e ingesta"])


# --- Semáforo: recálculo (5.5) ---------------------------------------------
@router.post(
    "/properties/{property_id}/traffic-light/recalculate",
    response_model=RecalculateResponse,
    summary="Forzar recálculo del semáforo",
    responses={403: {}, 404: {}},
)
async def recalculate(
    property_id: str, _: User = Depends(require_analyst), db: AsyncSession = Depends(get_db)
):
    result = await recalculate_traffic_light(db, property_id)
    if result is None:
        raise errors.not_found("Propiedad inexistente.")
    return RecalculateResponse(
        flag=result.flag,
        engine_version=result.engine_version,
        recalculated_at=result.generated_at.isoformat(),
    )


# --- Reglas del motor (5.5) -------------------------------------------------
@router.get("/rules", response_model=RuleList, summary="Listar reglas del motor",
            responses={403: {}})
async def list_rules(_: User = Depends(require_analyst), db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Rule))).scalars().all()
    return RuleList(items=[RuleItem.model_validate(r) for r in rows])


@router.post(
    "/rules",
    response_model=RuleItem,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una regla",
    responses={403: {}, 409: {"description": "Código duplicado"}, 422: {}},
)
async def create_rule(
    body: CreateRuleRequest, _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    dup = (
        await db.execute(select(Rule).where(Rule.code == body.code))
    ).scalar_one_or_none()
    if dup:
        raise errors.conflict("Ya existe una regla con ese código.")
    rule = Rule(
        code=body.code, severity=body.severity.value, description=body.description,
        title=body.title, message=body.message, condition=body.condition, active=body.active,
    )
    db.add(rule)
    await db.flush()
    return RuleItem.model_validate(rule)


@router.patch(
    "/rules/{rule_id}",
    response_model=RuleItem,
    summary="Actualizar una regla (severidad, condición, activación)",
    responses={403: {}, 404: {}},
)
async def update_rule(
    rule_id: str, body: UpdateRuleRequest, _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise errors.not_found("Regla inexistente.")
    if body.severity is not None:
        rule.severity = body.severity.value
    for field in ("description", "title", "message", "condition", "active"):
        val = getattr(body, field)
        if val is not None:
            setattr(rule, field, val)
    await db.flush()
    return RuleItem.model_validate(rule)


@router.delete(
    "/rules/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una regla",
    responses={403: {}, 404: {}},
)
async def delete_rule(
    rule_id: str, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    rule = await db.get(Rule, rule_id)
    if rule is None:
        raise errors.not_found("Regla inexistente.")
    await db.delete(rule)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Propiedades: alta/edición/baja (5.9) -----------------------------------
def _apply_block(target, block) -> None:
    if block is None:
        return
    for k, v in block.model_dump(exclude_unset=True).items():
        setattr(target, k, v)


@router.post(
    "/properties",
    response_model=PropertyMutationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear propiedad (dispara cálculo de semáforo)",
    responses={403: {}, 422: {}},
)
async def create_property(
    body: CreatePropertyRequest, _: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    prop = Property(
        address=body.address, city=body.city, zip=body.zip,
        county_id=body.county_id, property_type=body.property_type,
    )
    db.add(prop)
    await db.flush()

    fin = PropertyFinancial(property_id=prop.id)
    legal = PropertyLegal(property_id=prop.id)
    phys = PropertyPhysical(property_id=prop.id)
    _apply_block(fin, body.financial)
    _apply_block(legal, body.legal)
    _apply_block(phys, body.physical)
    db.add_all([fin, legal, phys])
    await db.flush()

    result = await recalculate_traffic_light(db, prop.id)
    return PropertyMutationResponse(id=prop.id, flag=result.flag if result else None)


@router.patch(
    "/properties/{property_id}",
    response_model=PropertyMutationResponse,
    summary="Actualizar propiedad (recalcula semáforo si cambian atributos relevantes)",
    responses={403: {}, 404: {}, 422: {}},
)
async def update_property(
    property_id: str, body: UpdatePropertyRequest, _: User = Depends(require_analyst),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy.orm import selectinload

    prop = (
        await db.execute(
            select(Property)
            .options(
                selectinload(Property.financial),
                selectinload(Property.legal),
                selectinload(Property.physical),
            )
            .where(Property.id == property_id)
        )
    ).scalar_one_or_none()
    if prop is None:
        raise errors.not_found("Propiedad inexistente.")

    for field in ("address", "city", "zip", "county_id", "property_type"):
        val = getattr(body, field)
        if val is not None:
            setattr(prop, field, val)
    _apply_block(prop.financial, body.financial)
    _apply_block(prop.legal, body.legal)
    _apply_block(prop.physical, body.physical)
    await db.flush()

    result = await recalculate_traffic_light(db, prop.id)
    return PropertyMutationResponse(id=prop.id, flag=result.flag if result else None)


@router.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar o archivar una propiedad",
    responses={403: {}, 404: {}},
)
async def delete_property(
    property_id: str, _: User = Depends(require_admin), db: AsyncSession = Depends(get_db)
):
    prop = await db.get(Property, property_id)
    if prop is None:
        raise errors.not_found("Propiedad inexistente.")
    prop.archived = True  # archivado (soft-delete)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Ingesta (5.9) ----------------------------------------------------------
@router.post(
    "/ingest",
    response_model=IngestJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar trabajo de ingesta de datos (asíncrono)",
    responses={403: {}, 422: {}},
)
async def start_ingest(
    body: IngestRequest, background: BackgroundTasks,
    _: User = Depends(require_analyst), db: AsyncSession = Depends(get_db),
):
    job = IngestJob(
        source=body.source, county_id=body.county_id, file_url=body.file_url, status="queued"
    )
    db.add(job)
    await db.flush()
    job_id = job.id
    background.add_task(jobs_service.run_ingest_job, job_id)
    return IngestJobResponse(job_id=job_id, status="queued")


@router.get(
    "/ingest/{job_id}",
    response_model=IngestJobStatus,
    summary="Consultar estado de un trabajo de ingesta",
    responses={403: {}, 404: {}},
)
async def ingest_status(
    job_id: str, _: User = Depends(require_analyst), db: AsyncSession = Depends(get_db)
):
    job = await db.get(IngestJob, job_id)
    if job is None:
        raise errors.not_found("Trabajo de ingesta inexistente.")
    return IngestJobStatus(
        job_id=job.id, status=job.status, created=job.created,
        updated=job.updated, failed=job.failed,
        finished_at=job.finished_at.isoformat() if job.finished_at else None,
    )
