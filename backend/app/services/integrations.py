"""Interfaces de integración externa con implementaciones *stub* conmutables.

Cada proveedor define una interfaz abstracta y una implementación stub que no
requiere credenciales (loguea/simula). Para producción, se implementa la clase
real y se conmuta mediante variables de entorno (SMS_PROVIDER, PUSH_PROVIDER,
OAUTH_PROVIDER_MODE). Los stubs permiten probar todos los flujos end-to-end.
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod

from app.core.config import settings

logger = logging.getLogger("integrations")


# --- SMS (2FA) --------------------------------------------------------------
class SMSProvider(ABC):
    @abstractmethod
    async def send(self, phone: str, message: str) -> None: ...


class StubSMSProvider(SMSProvider):
    """No envía SMS real; registra el mensaje. El código OTP viaja en el log."""

    async def send(self, phone: str, message: str) -> None:
        logger.info("[SMS-STUB] -> %s: %s", phone, message)


class TwilioSMSProvider(SMSProvider):  # pragma: no cover - requiere credenciales
    async def send(self, phone: str, message: str) -> None:
        # TODO: integrar SDK de Twilio usando settings.TWILIO_*
        raise NotImplementedError("Configurar Twilio para SMS_PROVIDER=twilio")


def get_sms_provider() -> SMSProvider:
    if settings.SMS_PROVIDER == "twilio":
        return TwilioSMSProvider()
    return StubSMSProvider()


# --- Push (FCM/APNs) --------------------------------------------------------
class PushProvider(ABC):
    @abstractmethod
    async def send(self, token: str, platform: str, title: str, body: str) -> None: ...


class StubPushProvider(PushProvider):
    async def send(self, token: str, platform: str, title: str, body: str) -> None:
        logger.info("[PUSH-STUB] -> %s (%s): %s / %s", token[:12], platform, title, body)


class FCMPushProvider(PushProvider):  # pragma: no cover
    async def send(self, token: str, platform: str, title: str, body: str) -> None:
        raise NotImplementedError("Configurar FCM/APNs para PUSH_PROVIDER=fcm")


def get_push_provider() -> PushProvider:
    if settings.PUSH_PROVIDER == "fcm":
        return FCMPushProvider()
    return StubPushProvider()


# --- OAuth (Google / Apple / Facebook) --------------------------------------
class OAuthUserInfo:
    """Datos normalizados devueltos por un proveedor OAuth tras verificar el token."""

    def __init__(self, provider: str, provider_uid: str, email: str | None,
                 first_name: str | None = None, last_name: str | None = None) -> None:
        self.provider = provider
        self.provider_uid = provider_uid
        self.email = email
        self.first_name = first_name
        self.last_name = last_name


class OAuthVerifier(ABC):
    @abstractmethod
    async def verify(self, provider: str, token: str) -> OAuthUserInfo:
        """Verifica el token del proveedor y devuelve la info del usuario.

        Lanza ValueError si el token es inválido.
        """


class StubOAuthVerifier(OAuthVerifier):
    """Acepta cualquier token no vacío y deriva una identidad determinista.

    Convención para pruebas: si el token contiene un email (formato
    'stub:<email>'), lo usa; en caso contrario genera uno a partir del hash.
    """

    async def verify(self, provider: str, token: str) -> OAuthUserInfo:
        if not token:
            raise ValueError("token de proveedor vacío")
        if token.startswith("stub:"):
            email = token.split("stub:", 1)[1]
            uid = f"{provider}_{email}"
        else:
            uid = f"{provider}_{abs(hash(token)) % (10**12)}"
            email = f"{uid}@oauth.stub"
        return OAuthUserInfo(
            provider=provider, provider_uid=uid, email=email,
            first_name="OAuth", last_name="User",
        )


class RealOAuthVerifier(OAuthVerifier):  # pragma: no cover - requiere JWKS
    async def verify(self, provider: str, token: str) -> OAuthUserInfo:
        # TODO: validar id_token contra los JWKS del proveedor
        # (Google/Apple) o el token de acceso (Facebook), comprobando
        # audience (client_id) y firma.
        raise NotImplementedError("Configurar OAUTH_PROVIDER_MODE=real")


def get_oauth_verifier() -> OAuthVerifier:
    if settings.OAUTH_PROVIDER_MODE == "real":
        return RealOAuthVerifier()
    return StubOAuthVerifier()
