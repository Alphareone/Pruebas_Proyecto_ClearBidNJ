# ClearBid NJ — Backend API

Backend de la **App de Oportunidades de Remate — New Jersey**.
FastAPI · Python 3.12 · PostgreSQL (SQLAlchemy 2.0 async + Alembic).

Implementa el catálogo completo de endpoints del documento
*Especificación de API v1.1*: autenticación y 2FA, usuarios/perfil, geografía,
propiedades, motor de semáforo y reglas, guardadas, cobertura, alertas,
administración/ingesta, utilidad y las capacidades de la interfaz web
(segmentos, exportación asíncrona, operaciones en lote y facetas).

## Puesta en marcha

### Opción A — Docker (recomendado)

```bash
docker compose up --build
```

Levanta PostgreSQL + la API, aplica migraciones y expone el servicio en
`http://localhost:8000`. Documentación interactiva en `/docs`.

### Opción B — Local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # ajusta DATABASE_URL y JWT_SECRET

# Con un PostgreSQL corriendo:
alembic upgrade head
uvicorn app.main:app --reload
```

## Documentación de la API

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

FastAPI genera el contrato OpenAPI automáticamente a partir de los schemas
Pydantic v2; cada endpoint incluye summary, descripción y códigos de estado.

## Autenticación

JWT con access token de corta duración (15 min) + refresh token con rotación.
2FA por SMS obligatorio tras el primer factor. Se envía el access token en el
header `Authorization: Bearer <access_token>`.

Flujo: `register`/`login` o `oauth/{provider}` → reto 2FA → `2fa/verify` (emite
tokens) → uso de la API → `token/refresh` para renovar.

## Integraciones externas (conmutables por entorno)

SMS (2FA), OAuth (Google/Apple/Facebook) y push (FCM/APNs) están detrás de
interfaces con implementación **stub** por defecto (no requieren credenciales y
permiten probar todos los flujos end-to-end). Para producción, se activan con:

```
SMS_PROVIDER=twilio
PUSH_PROVIDER=fcm
OAUTH_PROVIDER_MODE=real
```

En modo stub, el código OTP y el token de restablecimiento se registran en el
log (`[SMS-STUB]`, `[RESET-STUB]`).

## Motor de semáforo

`app/services/traffic_light.py` evalúa las reglas activas contra los atributos
de la propiedad. Regla `critical` que falla → **rojo**; `warning` → **amarillo**;
ninguna → **verde**. Las condiciones se expresan como expresiones sobre
`financial.*`, `legal.*` y `physical.*`, evaluadas en un sandbox restringido.
Se administran vía `/api/v1/admin/rules` y se recalculan con
`/api/v1/admin/properties/{id}/traffic-light/recalculate`.

## Roles

| Módulo | investor | analyst | admin |
|---|---|---|---|
| Auth / perfil / lectura de propiedades | ✔ | ✔ | ✔ |
| Guardadas / cobertura / alertas / segmentos / export | ✔ | ✔ | ✔ |
| Recalcular semáforo / crear-editar propiedades / ingesta | ✘ | ✔ | ✔ |
| Eliminar propiedades / administrar reglas | ✘ | ✘ | ✔ |

## Tests

```bash
pytest
```

Los tests usan SQLite en memoria (no requieren PostgreSQL) y cubren el flujo de
auth+2FA, filtros y paginación de propiedades, motor de semáforo, control de
roles y guardadas.

## Estructura

```
app/
  main.py              # app FastAPI, tags OpenAPI, montaje de routers
  core/                # config, seguridad (JWT/Argon2), deps, errores, paginación
  db/                  # base declarativa y sesión async
  models/              # modelos SQLAlchemy 2.0 (todas las tablas del contrato)
  schemas/             # schemas Pydantic v2 (request/response)
  services/            # motor de semáforo, integraciones (stub), auth, jobs, query
  api/v1/              # routers por módulo funcional
alembic/               # migraciones (0001_initial crea todo el esquema)
tests/                 # pytest (SQLite en memoria)
```

## Notas de implementación

- Trabajos asíncronos (ingesta, exportación) se ejecutan con `BackgroundTasks`.
  En producción, sustituir por Celery/RQ (ver `app/services/jobs_service.py`).
- Rate limiting de auth/2FA en memoria; para multi-instancia usar Redis
  (`app/services/rate_limit.py`).
- Índices sugeridos ya declarados en los modelos (county_id, flag, auction_date,
  opening_price). Para búsqueda de texto y mapa, considerar pg_trgm/PostGIS.
- Errores unificados con el formato `{ "error": { code, message, details } }`.
