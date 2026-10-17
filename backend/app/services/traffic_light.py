"""Motor de reglas del semáforo (verde / amarillo / rojo).

Evalúa las reglas activas contra los atributos de una propiedad y determina el
color agregado:
  - Si alguna regla `critical` falla  -> red
  - Si alguna regla `warning` falla   -> yellow
  - En caso contrario                 -> green

Las condiciones de las reglas se expresan como expresiones Python restringidas
(p. ej. "legal.surviving_irs_lien and legal.surviving_irs_lien > 0"). Se evalúan
en un sandbox sin builtins y con un contexto de solo lectura construido a partir
de la propiedad. Es un motor determinista y sin efectos secundarios.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

ENGINE_VERSION = "2.3"


@dataclass
class EvaluatedRule:
    code: str
    status: str      # pass | fail
    severity: str    # info | warning | critical
    title: str | None
    message: str | None


def _to_namespace(d: dict[str, Any] | None) -> SimpleNamespace:
    return SimpleNamespace(**(d or {}))


def build_context(prop: Any) -> dict[str, Any]:
    """Construye el contexto de evaluación a partir de un modelo Property.

    Acepta tanto objetos ORM como diccionarios (útil para tests).
    """
    def block(name: str) -> dict:
        obj = prop.get(name) if isinstance(prop, dict) else getattr(prop, name, None)
        if obj is None:
            return {}
        if isinstance(obj, dict):
            return obj
        # objeto ORM -> dict de columnas simples
        return {
            k: v for k, v in vars(obj).items() if not k.startswith("_")
        }

    return {
        "financial": _to_namespace(block("financial")),
        "legal": _to_namespace(block("legal")),
        "physical": _to_namespace(block("physical")),
    }


# builtins mínimos permitidos dentro del sandbox de condiciones
_SAFE_BUILTINS = {"len": len, "abs": abs, "min": min, "max": max, "round": round}


def _safe_eval(expr: str, ctx: dict[str, Any]) -> bool:
    try:
        return bool(eval(expr, {"__builtins__": _SAFE_BUILTINS}, ctx))  # noqa: S307
    except Exception:
        # Una condición que no puede evaluarse (datos faltantes) se considera "no cumplida".
        return False


def evaluate(prop: Any, rules: list[Any]) -> tuple[str, list[EvaluatedRule]]:
    """Evalúa las reglas y devuelve (flag, lista de resultados).

    `rules` es una lista de objetos con: code, severity, condition, title,
    message, active.
    """
    ctx = build_context(prop)
    results: list[EvaluatedRule] = []
    has_critical_fail = False
    has_warning_fail = False

    for rule in rules:
        active = rule.get("active") if isinstance(rule, dict) else getattr(rule, "active", True)
        if not active:
            continue
        code = rule["code"] if isinstance(rule, dict) else rule.code
        severity = rule["severity"] if isinstance(rule, dict) else rule.severity
        condition = rule["condition"] if isinstance(rule, dict) else rule.condition
        title = rule.get("title") if isinstance(rule, dict) else getattr(rule, "title", None)
        message = rule.get("message") if isinstance(rule, dict) else getattr(rule, "message", None)

        triggered = _safe_eval(condition, ctx)
        # Una condición "verdadera" significa que la regla se dispara = FAIL.
        status = "fail" if triggered else "pass"
        if triggered:
            if severity == "critical":
                has_critical_fail = True
            elif severity == "warning":
                has_warning_fail = True
        results.append(
            EvaluatedRule(
                code=code, status=status, severity=severity,
                title=title, message=message,
            )
        )

    if has_critical_fail:
        flag = "red"
    elif has_warning_fail:
        flag = "yellow"
    else:
        flag = "green"
    return flag, results


def now_tz() -> datetime:
    return datetime.now(timezone.utc)
