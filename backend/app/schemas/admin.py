"""Schemas de administración e ingesta (sección 5.9)."""
from pydantic import BaseModel, Field

from app.schemas.property import FinancialBlock, LegalBlock, PhysicalBlock


class CreatePropertyRequest(BaseModel):
    address: str
    city: str
    zip: str
    county_id: str
    property_type: str
    financial: FinancialBlock | None = None
    legal: LegalBlock | None = None
    physical: PhysicalBlock | None = None


class UpdatePropertyRequest(BaseModel):
    address: str | None = None
    city: str | None = None
    zip: str | None = None
    county_id: str | None = None
    property_type: str | None = None
    financial: FinancialBlock | None = None
    legal: LegalBlock | None = None
    physical: PhysicalBlock | None = None


class PropertyMutationResponse(BaseModel):
    id: str
    flag: str | None = None


class IngestRequest(BaseModel):
    source: str = Field(..., examples=["essex_sheriff_csv"])
    county_id: str
    file_url: str | None = None


class IngestJobResponse(BaseModel):
    job_id: str
    status: str


class IngestJobStatus(BaseModel):
    job_id: str
    status: str
    created: int = 0
    updated: int = 0
    failed: int = 0
    finished_at: str | None = None
