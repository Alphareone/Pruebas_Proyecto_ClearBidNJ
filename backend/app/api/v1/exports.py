"""Sección 6.3 — Exportación asíncrona (CSV / Excel)."""
import json

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.jobs import ExportJob
from app.models.user import User
from app.schemas.web import ExportJobResponse, ExportJobStatus, ExportRequest
from app.services import jobs_service

router = APIRouter(tags=["Exportación (web)"])


@router.post(
    "/properties/export",
    response_model=ExportJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Iniciar exportación (por IDs o filtro)",
    responses={401: {}, 422: {}},
)
async def start_export(
    body: ExportRequest, background: BackgroundTasks,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    params = {
        "property_ids": body.property_ids,
        "filters": body.filters.model_dump(exclude_none=True) if body.filters else None,
        "columns": body.columns,
    }
    job = ExportJob(
        user_id=user.id, format=body.format, status="queued", params=json.dumps(params)
    )
    db.add(job)
    await db.flush()
    job_id = job.id
    background.add_task(jobs_service.run_export_job, job_id)
    return ExportJobResponse(job_id=job_id, status="queued")


@router.get(
    "/exports/{job_id}",
    response_model=ExportJobStatus,
    summary="Estado del trabajo de exportación y URL de descarga",
    responses={404: {}},
)
async def export_status(
    job_id: str, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    job = await db.get(ExportJob, job_id)
    if job is None or job.user_id != user.id:
        raise errors.not_found("Trabajo de exportación inexistente.")
    return ExportJobStatus(
        job_id=job.id, status=job.status, row_count=job.row_count,
        download_url=job.download_url, expires_at=job.expires_at,
    )
