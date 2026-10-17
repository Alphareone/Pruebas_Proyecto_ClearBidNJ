"""Modelos del motor de semáforo: reglas, resultados y color por propiedad."""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.security import new_id
from app.db.base import Base, TimestampMixin


class Rule(Base, TimestampMixin):
    __tablename__ = "rules"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("rul"))
    code: Mapped[str] = mapped_column(String(60), unique=True, index=True, nullable=False)
    # info | warning | critical
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Expresión evaluable sobre atributos de la propiedad (sandbox restringido).
    condition: Mapped[str] = mapped_column(Text, nullable=False)
    # Mensaje mostrado cuando la condición se cumple (plantilla).
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class TrafficLightResult(Base, TimestampMixin):
    __tablename__ = "traffic_light_results"

    property_id: Mapped[str] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), primary_key=True
    )
    flag: Mapped[str] = mapped_column(String(10), nullable=False)  # green|yellow|red
    engine_version: Mapped[str] = mapped_column(String(10), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    rule_results: Mapped[list["RuleResult"]] = relationship(
        back_populates="result", cascade="all, delete-orphan"
    )


class RuleResult(Base):
    __tablename__ = "rule_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: new_id("rur"))
    property_id: Mapped[str] = mapped_column(
        ForeignKey("traffic_light_results.property_id", ondelete="CASCADE"), index=True
    )
    rule_code: Mapped[str] = mapped_column(String(60), nullable=False)
    status: Mapped[str] = mapped_column(String(10), nullable=False)  # pass|fail
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str | None] = mapped_column(String(160), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)

    result: Mapped["TrafficLightResult"] = relationship(back_populates="rule_results")
