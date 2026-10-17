"""Módulo 5.8 — Alertas, notificaciones y dispositivos."""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.core.pagination import PageParams
from app.db.session import get_db
from app.models.engagement import Alert
from app.models.user import AlertSetting, Device, User
from app.schemas.engagement import (
    AlertChannels,
    AlertItem,
    AlertList,
    AlertSettings,
    DeviceRequest,
    UpdateAlertRequest,
    UpdateAlertSettings,
)

router = APIRouter(tags=["Alertas y notificaciones"])


@router.get("/alerts", response_model=AlertList, summary="Listar alertas del usuario")
async def list_alerts(
    unread: bool | None = Query(None, description="Filtra no leídas."),
    page: PageParams = Depends(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Alert).where(Alert.user_id == user.id)
    if unread is not None:
        # unread=True -> read=False ; unread=False -> read=True
        stmt = stmt.where(Alert.read == (not unread))
    stmt = stmt.order_by(Alert.created_at.desc()).offset(page.offset).limit(page.limit)
    rows = (await db.execute(stmt)).scalars().all()
    unread_count = (
        await db.execute(
            select(func.count()).select_from(Alert).where(
                Alert.user_id == user.id, Alert.read.is_(False)
            )
        )
    ).scalar_one()
    return AlertList(
        items=[AlertItem.model_validate(a) for a in rows], unread_count=unread_count
    )


@router.patch(
    "/alerts/{alert_id}",
    response_model=AlertItem,
    summary="Marcar una alerta como leída/no leída",
    responses={404: {}},
)
async def update_alert(
    alert_id: str, body: UpdateAlertRequest,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    alert = await db.get(Alert, alert_id)
    if alert is None or alert.user_id != user.id:
        raise errors.not_found("Alerta inexistente.")
    alert.read = body.read
    return AlertItem.model_validate(alert)


@router.post("/alerts/read-all", summary="Marcar todas las alertas como leídas")
async def read_all(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    res = await db.execute(
        update(Alert)
        .where(Alert.user_id == user.id, Alert.read.is_(False))
        .values(read=True)
    )
    return {"updated": res.rowcount or 0}


@router.get(
    "/alerts/settings", response_model=AlertSettings, summary="Preferencias de notificación"
)
async def get_alert_settings(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    s = await db.get(AlertSetting, user.id)
    if s is None:
        s = AlertSetting(user_id=user.id)
        db.add(s)
        await db.flush()
    return AlertSettings(
        new_property=s.new_property, price_drop=s.price_drop,
        auction_reminder=s.auction_reminder,
        channels=AlertChannels(push=s.channel_push, email=s.channel_email, sms=s.channel_sms),
    )


@router.patch(
    "/alerts/settings",
    response_model=AlertSettings,
    summary="Actualizar preferencias de notificación",
    responses={422: {}},
)
async def update_alert_settings(
    body: UpdateAlertSettings,
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    s = await db.get(AlertSetting, user.id)
    if s is None:
        s = AlertSetting(user_id=user.id)
        db.add(s)
    if body.new_property is not None:
        s.new_property = body.new_property
    if body.price_drop is not None:
        s.price_drop = body.price_drop
    if body.auction_reminder is not None:
        s.auction_reminder = body.auction_reminder
    if body.channels:
        if "push" in body.channels:
            s.channel_push = bool(body.channels["push"])
        if "email" in body.channels:
            s.channel_email = bool(body.channels["email"])
        if "sms" in body.channels:
            s.channel_sms = bool(body.channels["sms"])
    await db.flush()
    return AlertSettings(
        new_property=s.new_property, price_drop=s.price_drop,
        auction_reminder=s.auction_reminder,
        channels=AlertChannels(push=s.channel_push, email=s.channel_email, sms=s.channel_sms),
    )


@router.post(
    "/devices",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar token push del dispositivo",
    responses={422: {}},
)
async def register_device(
    body: DeviceRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    existing = (
        await db.execute(select(Device).where(Device.token == body.token))
    ).scalar_one_or_none()
    if existing:
        existing.user_id = user.id
        existing.platform = body.platform
    else:
        db.add(Device(user_id=user.id, token=body.token, platform=body.platform))
    return {"registered": True}
