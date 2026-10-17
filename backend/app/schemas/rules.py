"""Schemas del motor de reglas (sección 5.5)."""
from pydantic import BaseModel, Field

from app.schemas.common import ORMModel, Severity


class RuleItem(ORMModel):
    id: str
    code: str
    severity: Severity
    active: bool
    description: str | None = None


class RuleList(BaseModel):
    items: list[RuleItem]


class CreateRuleRequest(BaseModel):
    code: str = Field(..., examples=["flood_zone_high"])
    severity: Severity
    description: str | None = None
    title: str | None = None
    message: str | None = None
    condition: str = Field(
        ...,
        description="Expresión evaluable sobre atributos de la propiedad.",
        examples=["physical.flood_zone in ['AE','VE']"],
    )
    active: bool = True


class UpdateRuleRequest(BaseModel):
    severity: Severity | None = None
    description: str | None = None
    title: str | None = None
    message: str | None = None
    condition: str | None = None
    active: bool | None = None


class RecalculateResponse(BaseModel):
    flag: str
    engine_version: str
    recalculated_at: str
