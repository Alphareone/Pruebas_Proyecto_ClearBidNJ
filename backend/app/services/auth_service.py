"""Lógica de apoyo para autenticación, 2FA y tokens."""
import hashlib
import secrets
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import OtpChallenge, PasswordResetToken, RefreshToken


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def mask_phone(phone: str | None) -> str | None:
    """Enmascara un teléfono E.164 -> '+1 (201) •••-0199'."""
    if not phone:
        return None
    digits = phone.lstrip("+")
    if len(digits) < 4:
        return "•••"
    last4 = digits[-4:]
    # Heurística simple para formato NANP (+1 AAA XXX-YYYY)
    if digits.startswith("1") and len(digits) == 11:
        area = digits[1:4]
        return f"+1 ({area}) •••-{last4}"
    return f"+{digits[:2]}••••{last4}"


def send_email_otp(to_email: str, code: str) -> None:
    """Envía el código de verificación por correo electrónico usando SMTP."""
    smtp_user = getattr(settings, "SMTP_USER", None)
    smtp_host = getattr(settings, "SMTP_HOST", None)
    smtp_port = getattr(settings, "SMTP_PORT", 587)
    smtp_pass = getattr(settings, "SMTP_PASSWORD", None)

    # Si no están configuradas las credenciales SMTP en el .env, usa el modo Stub
    if not smtp_user or not smtp_host:
        print(f"[EMAIL-STUB] Para {to_email}: Tu código ClearBid NJ es {code}")
        return

    try:
        msg = MIMEMultipart()
        sender_name = getattr(settings, "EMAILS_FROM_NAME", "ClearBid NJ")
        msg["From"] = f"{sender_name} <{smtp_user}>"
        msg["To"] = to_email
        msg["Subject"] = f"Código de verificación ClearBid NJ: {code}"

        body = f"""
Hola,

Tu código de verificación para ClearBid NJ es: {code}

Este código caducará en 5 minutos.
Si no solicitaste este código, puedes ignorar este mensaje.
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(smtp_host, int(smtp_port))
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        print(f"[EMAIL-SUCCESS] Código enviado correctamente a {to_email}")
    except Exception as e:
        print(f"[EMAIL-ERROR] Fallo al enviar correo a {to_email}: {e}")
        # Muestra el código en la consola si falla la conexión SMTP
        print(f"[EMAIL-FALLBACK] Código para {to_email}: {code}")


async def create_otp_challenge(
    db: AsyncSession, user, purpose: str = "login", pending_phone: str | None = None
) -> tuple[OtpChallenge, str]:
    """Crea un reto OTP, lo persiste y envía el código por correo electrónico."""
    code = "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))
    challenge = OtpChallenge(
        user_id=user.id,
        code_hash=_sha256(code),
        purpose=purpose,
        method="email",
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.OTP_EXPIRE_SECONDS),
        pending_phone=pending_phone,
    )
    db.add(challenge)
    await db.flush()

    # Se prioriza el envío al correo electrónico del usuario
    target_email = getattr(user, "email", None)
    if target_email:
        send_email_otp(target_email, code)

    return challenge, code


async def resend_otp(db: AsyncSession, challenge: OtpChallenge, user) -> None:
    """Regenera el código de un reto existente y lo reenvía por correo."""
    code = "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))
    challenge.code_hash = _sha256(code)
    challenge.attempts = 0
    challenge.expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.OTP_EXPIRE_SECONDS
    )
    
    target_email = getattr(user, "email", None)
    if target_email:
        send_email_otp(target_email, code)


def verify_otp_code(challenge: OtpChallenge, code: str) -> str:
    """Valida un código contra el reto. Devuelve 'ok' | 'expired' | 'invalid'."""
    now = datetime.now(timezone.utc)
    expires = challenge.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if challenge.consumed or now > expires:
        return "expired"
    if challenge.attempts >= settings.OTP_MAX_ATTEMPTS:
        return "expired"
    if challenge.code_hash != _sha256(code):
        challenge.attempts += 1
        return "invalid"
    return "ok"


async def issue_refresh_token(db: AsyncSession, user_id: str) -> RefreshToken:
    """Crea y persiste un refresh token, devolviendo el registro (con jti)."""
    token = RefreshToken(
        user_id=user_id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(token)
    await db.flush()
    return token


async def create_password_reset(db: AsyncSession, user_id: str) -> str:
    """Crea un token de restablecimiento y devuelve el valor en claro."""
    raw = "prt_" + secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            user_id=user_id,
            token_hash=_sha256(raw),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=settings.PASSWORD_RESET_EXPIRE_MINUTES),
        )
    )
    return raw


async def find_valid_reset(db: AsyncSession, raw_token: str) -> PasswordResetToken | None:
    res = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == _sha256(raw_token),
            PasswordResetToken.used.is_(False),
        )
    )
    prt = res.scalar_one_or_none()
    if prt is None:
        return None
    expires = prt.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires:
        return None
    return prt