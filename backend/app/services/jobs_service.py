"""Servicios de trabajos asíncronos: exportación e ingesta.

En este entregable los trabajos se ejecutan de forma inmediata mediante
BackgroundTasks de FastAPI para mantener el flujo end-to-end sin infraestructura
adicional. En producción, reemplazar por Celery/RQ (ver notas del contrato).
"""
import csv
import io
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.models.jobs import ExportJob, IngestJob
from app.models.property import Property, PropertyFinancial


async def run_export_job(job_id: str) -> None:
    """Procesa un trabajo de exportación (se invoca en background)."""
    async with AsyncSessionLocal() as db:
        job = await db.get(ExportJob, job_id)
        if job is None:
            return
        job.status = "processing"
        await db.commit()

        params = json.loads(job.params or "{}")
        columns = params.get("columns") or [
            "address", "city", "zip", "flag", "opening_price", "arv", "auction_date"
        ]
        stmt = select(Property).where(Property.archived.is_(False))
        if params.get("property_ids"):
            stmt = stmt.where(Property.id.in_(params["property_ids"]))
        rows = (await db.execute(stmt)).scalars().all()

        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(columns)
        for p in rows:
            fin = await db.get(PropertyFinancial, p.id)
            record = {
                "address": p.address, "city": p.city, "zip": p.zip,
                "flag": p.flag,
                "opening_price": getattr(fin, "opening_price", None),
                "arv": getattr(fin, "arv", None),
                "roi": getattr(fin, "estimated_roi", None),
                "auction_date": None,
            }
            writer.writerow([record.get(c) for c in columns])

        job.status = "completed"
        job.row_count = len(rows)
        job.download_url = f"{settings.EXPORT_URL_BASE}/{job.id}.{job.format}"
        job.expires_at = datetime.now(timezone.utc) + timedelta(hours=6)
        await db.commit()


async def run_ingest_job(job_id: str) -> None:
    """Simula el procesamiento de un trabajo de ingesta (se invoca en background)."""
    async with AsyncSessionLocal() as db:
        job = await db.get(IngestJob, job_id)
        if job is None:
            return
        job.status = "processing"
        await db.commit()
        # TODO: descargar file_url, parsear según `source`, upsert de propiedades
        # y disparar recálculo de semáforo. Aquí solo marcamos el job completo.
        job.status = "completed"
        job.created = 0
        job.updated = 0
        job.failed = 0
        job.finished_at = datetime.now(timezone.utc)
        await db.commit()
