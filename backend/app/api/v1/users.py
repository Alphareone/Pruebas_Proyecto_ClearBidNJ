"""Módulo 5.2 — Usuarios y perfil."""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import errors
from app.core.deps import get_current_user
from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models.user import OAuthAccount, OtpChallenge, User, UserPreference
from app.schemas.user import (
    ChangePasswordRequest,
    Preferences,
    UpdatePreferencesRequest,
    UpdateProfileRequest,
    UserProfile,
    VerifyPhoneRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["Usuarios y perfil"])


async def _providers(db: AsyncSession, user_id: str) -> list[str]:
    res = await db.execute(
        select(OAuthAccount.provider).where(OAuthAccount.user_id == user_id)
    )
    return [p for (p,) in res.all()]


@router.get("/me", response_model=UserProfile, summary="Perfil del usuario autenticado")
async def get_me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    profile = UserProfile.model_validate(user)
    profile.auth_providers = await _providers(db, user.id)
    return profile


@router.patch(
    "/me",
    response_model=UserProfile,
    summary="Actualizar perfil",
    description="Cambiar email o teléfono marca el campo como no verificado y dispara "
    "reverificación.",
    responses={409: {"description": "Email en uso"}, 422: {}},
)
async def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.email and body.email != user.email:
        dup = (
            await db.execute(select(User).where(User.email == body.email))
        ).scalar_one_or_none()
        if dup:
            raise errors.conflict("El email ya está en uso.")
        user.email = body.email
    if body.first_name is not None:
        user.first_name = body.first_name
    if body.last_name is not None:
        user.last_name = body.last_name
    if body.phone and body.phone != user.phone:
        # Marca no verificado y dispara reverificación por SMS
        user.phone = body.phone
        user.phone_verified = False
        await auth_service.create_otp_challenge(
            db, user, purpose="phone_change", pending_phone=body.phone
        )
    profile = UserProfile.model_validate(user)
    profile.auth_providers = await _providers(db, user.id)
    return profile


@router.post(
    "/me/password",
    summary="Cambiar contraseña",
    responses={401: {"description": "Contraseña actual incorrecta"}, 422: {}},
)
async def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if user.password_hash is None or not verify_password(
        body.current_password, user.password_hash
    ):
        raise errors.unauthorized("La contraseña actual es incorrecta.")
    user.password_hash = hash_password(body.new_password)
    return {"changed": True}


@router.post(
    "/me/phone/verify",
    summary="Verificar nuevo teléfono con código SMS",
    responses={401: {"description": "Código inválido"}, 410: {"description": "Expirado"}},
)
async def verify_phone(
    body: VerifyPhoneRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    challenge = (
        await db.execute(
            select(OtpChallenge)
            .where(
                OtpChallenge.user_id == user.id,
                OtpChallenge.purpose == "phone_change",
                OtpChallenge.consumed.is_(False),
            )
            .order_by(OtpChallenge.created_at.desc())
        )
    ).scalars().first()
    if challenge is None:
        raise errors.not_found("No hay verificación de teléfono pendiente.")

    result = auth_service.verify_otp_code(challenge, body.code)
    if result == "expired":
        raise errors.gone("El código ha expirado.")
    if result == "invalid":
        raise errors.unauthorized("Código inválido.")

    challenge.consumed = True
    if challenge.pending_phone:
        user.phone = challenge.pending_phone
    user.phone_verified = True
    return {"phone_verified": True}


@router.get("/me/preferences", response_model=Preferences, summary="Obtener preferencias")
async def get_preferences(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    pref = await db.get(UserPreference, user.id)
    if pref is None:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
        await db.flush()
    return Preferences(language=pref.language, theme=pref.theme)


@router.patch(
    "/me/preferences", response_model=Preferences, summary="Actualizar preferencias",
    responses={422: {}},
)
async def update_preferences(
    body: UpdatePreferencesRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    pref = await db.get(UserPreference, user.id)
    if pref is None:
        pref = UserPreference(user_id=user.id)
        db.add(pref)
    if body.language is not None:
        pref.language = body.language.value
    if body.theme is not None:
        pref.theme = body.theme.value
    await db.flush()
    return Preferences(language=pref.language, theme=pref.theme)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar/anonimizar cuenta",
)
async def delete_me(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    from datetime import datetime, timezone

    # Anonimización: se conserva la fila pero se limpian datos personales.
    user.deleted_at = datetime.now(timezone.utc)
    user.is_active = False
    user.email = f"deleted+{user.id}@clearbid-nj.com"
    user.phone = None
    user.first_name = "Cuenta"
    user.last_name = "Eliminada"
    user.password_hash = None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
