"""Formato de error consistente y handlers globales (sección 3.3 del contrato).

Todos los errores devuelven:
    { "error": { "code": ..., "message": ..., "details": [...] } }
"""
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class APIError(Exception):
    """Excepción de dominio que se serializa al formato estándar de error."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


def _body(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "details": details or []}}


# --- Atajos de errores frecuentes -------------------------------------------
def not_found(message: str = "Recurso inexistente.") -> APIError:
    return APIError(status.HTTP_404_NOT_FOUND, "not_found", message)


def conflict(message: str, details: list[dict] | None = None) -> APIError:
    return APIError(status.HTTP_409_CONFLICT, "conflict", message, details)


def unauthorized(message: str = "Falta o expiró el token.") -> APIError:
    return APIError(status.HTTP_401_UNAUTHORIZED, "unauthorized", message)


def forbidden(message: str = "Permisos insuficientes.") -> APIError:
    return APIError(status.HTTP_403_FORBIDDEN, "forbidden", message)


def gone(message: str = "El recurso ha expirado.") -> APIError:
    return APIError(status.HTTP_410_GONE, "gone", message)


def bad_request(message: str, details: list[dict] | None = None) -> APIError:
    return APIError(status.HTTP_400_BAD_REQUEST, "bad_request", message, details)


def rate_limited(retry_after: int = 60) -> APIError:
    err = APIError(
        status.HTTP_429_TOO_MANY_REQUESTS,
        "rate_limited",
        "Límite de tasa excedido. Intente más tarde.",
    )
    err.retry_after = retry_after  # type: ignore[attr-defined]
    return err


def unprocessable(message: str, details: list[dict] | None = None) -> APIError:
    return APIError(
        status.HTTP_422_UNPROCESSABLE_ENTITY, "validation_error", message, details
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los handlers que unifican el cuerpo de error."""

    @app.exception_handler(APIError)
    async def _api_error(_: Request, exc: APIError) -> JSONResponse:
        headers = {}
        if exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            headers["Retry-After"] = str(getattr(exc, "retry_after", 60))
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(exc.code, exc.message, exc.details),
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(p) for p in e["loc"] if p != "body"), "issue": e["type"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_body("validation_error", "Error de validación del esquema.", details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code_map = {
            400: "bad_request", 401: "unauthorized", 403: "forbidden",
            404: "not_found", 409: "conflict", 410: "gone", 429: "rate_limited",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=_body(code_map.get(exc.status_code, "error"), str(exc.detail)),
        )
