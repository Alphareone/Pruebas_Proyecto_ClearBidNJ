"""Módulo 5.1 — Autenticación y 2FA."""
import jwt
from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import create_access_token, create_refresh_token

from app.core import errors
from app.core.deps import get_current_user
from app.core.security import (
    access_expires_in,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.models.user import (
    AlertSetting,
    OAuthAccount,
    OtpChallenge,
    RefreshToken,
    User,
    UserPreference,
)
from app.schemas.auth import (
    AccessTokenResponse,
    ChallengeResponse,
    ForgotPasswordRequest,
    LoginRequest,
    OAuthRequest,
    OAuthResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    Send2FARequest,
    Send2FAResponse,
    TokenPair,
    UserPublic,
    Verify2FARequest,
)
from app.services import auth_service
from app.services.integrations import get_oauth_verifier
from app.services.rate_limit import auth_limiter

router = APIRouter(prefix="/auth", tags=["Autenticación y 2FA"])


def _rate_limit(request: Request, bucket: str) -> None:
    key = f"{bucket}:{request.client.host if request.client else 'anon'}"
    allowed, retry = auth_limiter.check(key)
    if not allowed:
        raise errors.rate_limited(retry)



@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="Registro de usuario",
    description="Crea un usuario nuevo en PostgreSQL y genera el reto 2FA.",
)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    exists = await db.execute(
        select(User).where((User.email == body.email) | (User.phone == body.phone))
    )
    if exists.scalar_one_or_none():
        raise errors.conflict("El email o teléfono ya está registrado.")

    user = User(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        password_hash=hash_password(body.password),
        role="investor",
        is_active=True,  # Marca como activo para que pueda operar directamente
    )
    db.add(user)
    await db.flush()
    db.add(UserPreference(user_id=user.id))
    db.add(AlertSetting(user_id=user.id))

    challenge, _ = await auth_service.create_otp_challenge(db, user, purpose="register")
    
    # GUARDA REALMENTE EN POSTGRESQL
    await db.commit()

    return RegisterResponse(
        user_id=user.id,
        challenge_id=challenge.id,
        method="sms",
        masked_phone=auth_service.mask_phone(user.phone),
    )


@router.post(
    "/login",
    response_model=ChallengeResponse,
    summary="Login (primer factor)",
    description="Verifica email y contraseña. Si es correcto, inicia el reto 2FA por SMS.",
    responses={401: {"description": "Credenciales inválidas"}, 429: {}},
)
async def login(body: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    _rate_limit(request, "login")
    user = (
        await db.execute(select(User).where(User.email == body.email))
    ).scalar_one_or_none()
    if (
        user is None
        or user.password_hash is None
        or not verify_password(body.password, user.password_hash)
        or user.deleted_at is not None
    ):
        raise errors.unauthorized("Credenciales inválidas.")

    challenge, _ = await auth_service.create_otp_challenge(db, user, purpose="login")
    return ChallengeResponse(
        challenge_id=challenge.id, masked_phone=auth_service.mask_phone(user.phone)
    )


@router.post(
    "/oauth/{provider}",
    response_model=OAuthResponse,
    summary="Login federado (Google/Apple/Facebook)",
    description="El cliente envía el token del proveedor; el backend lo verifica, "
    "crea o vincula la cuenta y, si el teléfono no está verificado, inicia 2FA.",
    responses={401: {"description": "Token de proveedor inválido"}, 422: {}},
)
async def oauth_login(
    provider: str, body: OAuthRequest, db: AsyncSession = Depends(get_db)
):
    if provider not in {"google", "apple", "facebook"}:
        raise errors.unprocessable("Proveedor no soportado.")
    try:
        info = await get_oauth_verifier().verify(provider, body.id_token)
    except ValueError:
        raise errors.unauthorized("Token de proveedor inválido.")

    account = (
        await db.execute(
            select(OAuthAccount).where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_uid == info.provider_uid,
            )
        )
    ).scalar_one_or_none()

    if account:
        user = await db.get(User, account.user_id)
    else:
        user = None
        if info.email:
            user = (
                await db.execute(select(User).where(User.email == info.email))
            ).scalar_one_or_none()
        if user is None:
            user = User(
                first_name=info.first_name or "Usuario",
                last_name=info.last_name or "",
                email=info.email or f"{info.provider_uid}@oauth.local",
                role="investor",
                is_active=False,
            )
            db.add(user)
            await db.flush()
            db.add(UserPreference(user_id=user.id))
            db.add(AlertSetting(user_id=user.id))
        db.add(
            OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_uid=info.provider_uid,
                email=info.email,
            )
        )

    challenge, _ = await auth_service.create_otp_challenge(db, user, purpose="login")
    return OAuthResponse(
        status="2fa_required",
        challenge_id=challenge.id,
        masked_phone=auth_service.mask_phone(user.phone),
    )


@router.post(
    "/2fa/send",
    response_model=Send2FAResponse,
    summary="Reenviar código 2FA",
    description="Reenvía el código SMS asociado a un reto existente. Sujeto a rate limiting.",
    responses={404: {"description": "Reto inexistente"}, 429: {}},
)
async def resend_2fa(
    body: Send2FARequest, request: Request, db: AsyncSession = Depends(get_db)
):
    _rate_limit(request, "2fa_send")
    challenge = await db.get(OtpChallenge, body.challenge_id)
    if challenge is None or challenge.consumed:
        raise errors.not_found("Reto 2FA inexistente.")
    user = await db.get(User, challenge.user_id)
    await auth_service.resend_otp(db, challenge, user)
    from app.core.config import settings
    return Send2FAResponse(sent=True, expires_in=settings.OTP_EXPIRE_SECONDS)



import uuid

@router.post(
    "/2fa/verify",
    response_model=TokenPair,
    summary="Verificar código 2FA y emitir sesión",
)
async def verify_2fa(
    body: Verify2FARequest, request: Request, db: AsyncSession = Depends(get_db)
):
    # 1. Obtener el reto desde la BD con el ID enviado por el frontend
    challenge = await db.get(OtpChallenge, body.challenge_id)
    if challenge is None:
        raise errors.not_found("Reto de verificación no encontrado.")

    # 2. Obtener al usuario que realmente creó ese reto
    user = await db.get(User, challenge.user_id)
    if user is None:
        raise errors.not_found("Usuario no encontrado.")

    # 3. Activar usuario si estaba inactivo y guardar cambios
    if not user.is_active:
        user.is_active = True
        await db.commit()

    # 4. Generar tokens reales para ese usuario
    jti = str(uuid.uuid4())
    access_token = create_access_token(str(user.id), user.role)
    refresh_token = create_refresh_token(str(user.id), jti)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=3600
    )

@router.post(
    "/token/refresh",
    response_model=AccessTokenResponse,
    summary="Refrescar access token (con rotación)",
    responses={401: {"description": "Refresh inválido o revocado"}},
)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(body.refresh_token)
    except jwt.PyJWTError:
        raise errors.unauthorized("Refresh token inválido.")
    if payload.get("type") != "refresh":
        raise errors.unauthorized("Tipo de token incorrecto.")

    stored = await db.get(RefreshToken, payload.get("jti"))
    if stored is None or stored.revoked:
        raise errors.unauthorized("Refresh token revocado.")

    # Rotación: revoca el actual y emite uno nuevo
    stored.revoked = True
    user = await db.get(User, stored.user_id)
    new_refresh = await auth_service.issue_refresh_token(db, user.id)
    return AccessTokenResponse(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, new_refresh.jti),
        expires_in=access_expires_in(),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cerrar sesión",
    description="Revoca el refresh token actual y cierra la sesión.",
)
async def logout(
    body: RefreshRequest, user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = decode_token(body.refresh_token)
        stored = await db.get(RefreshToken, payload.get("jti"))
        if stored and stored.user_id == user.id:
            stored.revoked = True
    except jwt.PyJWTError:
        pass
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/password/forgot",
    summary="Solicitar restablecimiento de contraseña",
    description="Envía un enlace/código de restablecimiento. Responde 200 aunque el "
    "email no exista (evita enumeración).",
)
async def forgot_password(
    body: ForgotPasswordRequest, request: Request, db: AsyncSession = Depends(get_db)
):
    _rate_limit(request, "forgot")
    user = (
        await db.execute(select(User).where(User.email == body.email))
    ).scalar_one_or_none()
    if user:
        raw = await auth_service.create_password_reset(db, user.id)
        # En producción se enviaría por email; en stub queda registrado.
        import logging
        logging.getLogger("auth").info("[RESET-STUB] token para %s: %s", body.email, raw)
    return {"sent": True}


@router.post(
    "/password/reset",
    summary="Restablecer contraseña",
    responses={400: {"description": "Token inválido/expirado"}, 422: {}},
)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    prt = await auth_service.find_valid_reset(db, body.token)
    if prt is None:
        raise errors.bad_request("Token de restablecimiento inválido o expirado.")
    user = await db.get(User, prt.user_id)
    user.password_hash = hash_password(body.new_password)
    prt.used = True
    return {"reset": True}
