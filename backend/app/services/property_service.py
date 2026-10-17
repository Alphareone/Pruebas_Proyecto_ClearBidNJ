"""Servicios de propiedades: recálculo y persistencia del semáforo."""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.property import Property
from app.models.rules import Rule, RuleResult, TrafficLightResult
from app.services import traffic_light


async def recalculate_traffic_light(
    db: AsyncSession, property_id: str
) -> TrafficLightResult | None:
    """Recalcula el semáforo de una propiedad, persiste resultados y flag.

    Devuelve el TrafficLightResult resultante, o None si la propiedad no existe.
    """
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
        return None

    rules = (
        await db.execute(select(Rule).where(Rule.active.is_(True)))
    ).scalars().all()

    flag, evaluated = traffic_light.evaluate(prop, rules)
    generated_at = traffic_light.now_tz()

    # Upsert del resultado agregado
    result = await db.get(TrafficLightResult, property_id)
    if result is None:
        result = TrafficLightResult(property_id=property_id)
        db.add(result)
    result.flag = flag
    result.engine_version = traffic_light.ENGINE_VERSION
    result.generated_at = generated_at

    # Reemplaza los resultados por regla
    await db.execute(
        delete(RuleResult).where(RuleResult.property_id == property_id)
    )
    for er in evaluated:
        db.add(
            RuleResult(
                property_id=property_id,
                rule_code=er.code,
                status=er.status,
                severity=er.severity,
                title=er.title,
                message=er.message,
            )
        )

    # Denormaliza el flag en la propiedad para filtrar/ordenar rápido
    prop.flag = flag
    await db.flush()
    return result
