"""Schemas de la interfaz web: segmentos, exportación, batch y facetas (sección 6)."""
from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class PropertyFilter(BaseModel):
    """Objeto de filtro compartido (sección 6.1)."""
    flag: list[str] | None = None
    county_id: list[str] | None = None
    auction_type: list[str] | None = None
    property_type: list[str] | None = None
    min_opening: int | None = None
    max_opening: int | None = None
    min_roi: float | None = None
    q: str | None = None


# --- Segmentos --------------------------------------------------------------
class SegmentItem(BaseModel):
    id: str
    name: str
    filters: dict = {}
    alert_enabled: bool = False
    match_count: int = 0
    created_at: datetime | None = None


class SegmentList(BaseModel):
    items: list[SegmentItem]


class CreateSegmentRequest(BaseModel):
    name: str
    filters: PropertyFilter = PropertyFilter()
    alert_enabled: bool = False


class UpdateSegmentRequest(BaseModel):
    name: str | None = None
    filters: PropertyFilter | None = None
    alert_enabled: bool | None = None


class SegmentMutationResponse(BaseModel):
    id: str
    name: str | None = None
    match_count: int


# --- Exportación ------------------------------------------------------------
class ExportRequest(BaseModel):
    format: str = Field("csv", pattern="^(csv|xlsx)$")
    property_ids: list[str] | None = None
    filters: PropertyFilter | None = None
    columns: list[str] | None = None

    @model_validator(mode="after")
    def _require_selection(self) -> "ExportRequest":
        if not self.property_ids and not self.filters:
            raise ValueError("Debe enviar 'property_ids' o 'filters'.")
        return self


class ExportJobResponse(BaseModel):
    job_id: str
    status: str


class ExportJobStatus(BaseModel):
    job_id: str
    status: str
    row_count: int | None = None
    download_url: str | None = None
    expires_at: datetime | None = None


# --- Batch de favoritos -----------------------------------------------------
class SavedBatchRequest(BaseModel):
    action: str = Field(..., pattern="^(add|remove)$")
    property_ids: list[str] | None = None
    filters: PropertyFilter | None = None


class SavedBatchResponse(BaseModel):
    added: int = 0
    removed: int = 0
    total_saved: int = 0


# --- Facetas ----------------------------------------------------------------
class FacetsResponse(BaseModel):
    total: int
    flag: dict = {}
    county: list[dict] = []
    auction_type: dict = {}
    property_type: dict = {}
    roi_buckets: list[dict] = []
