# ClearBid NJ — guía de implementación

Este documento describe cómo está organizado el MVP, cómo ejecutarlo en un PC con Windows y cómo se conecta a la base de datos alojada en Supabase. Refleja el código revisado; señala también las partes que todavía son de demostración o requieren trabajo.

## 1. Arquitectura

ClearBid NJ tiene tres piezas principales:

| Pieza | Tecnología | Función |
|---|---|---|
| Interfaz web | React 18, TypeScript y Vite | Dashboard de propiedades, filtros, tabla/tarjetas/mapa, detalle, guardados, alertas, perfil y configuración. |
| API | FastAPI, Python 3.12 y SQLAlchemy asíncrono | Autenticación, endpoints, filtros, autorización y lectura/escritura de datos. |
| Base de datos | PostgreSQL administrado por Supabase | Conserva usuarios, propiedades, datos financieros/legales/físicos y demás entidades. |

El recorrido de una consulta es:

```text
Navegador (React) → API FastAPI (localhost:8000) → PostgreSQL de Supabase
```

En desarrollo, Vite envía las solicitudes `/api` al backend local. El navegador no se conecta directamente a Supabase y no utiliza la clave `anon` para cargar el dashboard.

## 2. Estructura del repositorio

```text
backend/
  app/api/v1/       Endpoints agrupados por módulo
  app/core/         Configuración, JWT, autorización y errores
  app/db/           Engine y sesiones SQLAlchemy
  app/models/       Modelos de PostgreSQL
  app/schemas/      Contratos Pydantic de entrada/salida
  app/services/     Autenticación, consultas, semáforo e integraciones
  alembic/          Migraciones de base de datos
  tests/            Pruebas automatizadas
  Dockerfile
  docker-compose.yml
web/
  src/pages/        Pantallas
  src/components/   Componentes de interfaz
  src/hooks/        Consultas a la API y estado de datos
  src/lib/api.ts    Cliente HTTP y renovación de JWT
```

## 3. Requisitos para ejecutar localmente

- Windows 10/11.
- Docker Desktop iniciado (para API, Redis y worker).
- Node.js y npm (para la interfaz web).
- Acceso de red al proyecto Supabase y una URL válida de PostgreSQL.

El `docker-compose.yml` actual **no crea un PostgreSQL local**. La API Dockerizada se conecta a Supabase. Por eso, que la interfaz y la API estén en tu PC no significa que los datos estén guardados en el PC.

Las notas entregadas indican que el despliegue previsto es en la nube y que se eligió Docker para correr la API local conectada directamente a Supabase. Ejecutarla fuera de Docker puede requerir una configuración distinta de Python, PostgreSQL y variables de entorno.

### 3.1 Iniciar backend y servicios

Abre PowerShell y ejecuta:

```powershell
cd "C:\Users\ferna\Desktop\Pruebas_Proyecto_ClearBidNJ-main\backend"
docker compose up --build
```

Docker inicia la API en `http://localhost:8000`, Redis y el worker. El Dockerfile ejecuta `alembic upgrade head` antes de iniciar FastAPI. La documentación interactiva está en `http://localhost:8000/docs` y la sonda de salud en `http://localhost:8000/health`.

La guía local entregada propone abrir la carpeta del proyecto en Visual Studio Code, abrir una terminal integrada, entrar a `backend` y ejecutar `docker compose up`. La primera compilación puede tardar porque Docker descarga la imagen de Python y las dependencias; las siguientes suelen reutilizar lo descargado. `docker compose up --build` fuerza la reconstrucción descrita arriba.

Para detener los servicios, usa `Ctrl+C`. Para dejarlos ejecutándose en segundo plano, puedes usar `docker compose up --build -d`; para detenerlos después, desde `backend`, ejecuta `docker compose down`.

### 3.2 Iniciar la interfaz web

Abre una segunda ventana de PowerShell:

```powershell
cd "C:\Users\ferna\Desktop\Pruebas_Proyecto_ClearBidNJ-main\web"
npm install
npm run dev
```

Abre la dirección que imprima Vite; normalmente `http://localhost:5173`. Mantén ambas terminales abiertas mientras trabajas. En desarrollo, `web/vite.config.ts` configura el proxy de `/api` hacia `http://localhost:8000`.

La instalación de dependencias ya se realizó en esta máquina. En el futuro, `npm install` solo hace falta al preparar otra copia o cuando cambian las dependencias.

## 4. Conexión con Supabase

### 4.1 Conexión que usa el MVP

El backend usa SQLAlchemy y `asyncpg` para conectarse directamente a PostgreSQL. La variable de configuración es `DATABASE_URL`, con el formato:

```text
postgresql+asyncpg://USUARIO:CONTRASEÑA@HOST:PUERTO/BASE
```

En Docker, esa variable se configura en `backend/docker-compose.yml` y apunta al pooler de Supabase. Las migraciones de Alembic crean el esquema esperado por los modelos del backend. La conexión debe conservarse solo en el servidor/backend.

Las notas del proyecto dicen que se cambió la configuración de red de Supabase a IPv4 por una limitación/costo asociado a IPv6. La URL configurada en Compose debe corresponder al endpoint/pooler habilitado para la red elegida. Si Supabase no conecta, verifica el host y modo de conexión en **Project Settings → Database → Connect**; no adivines ni publiques la URL completa.

La contraseña de base de datos es necesaria para la conexión directa del backend. Si contiene caracteres reservados para URLs, deben codificarse correctamente al construir `DATABASE_URL`. La clave `anon` no reemplaza esa contraseña.

La clave pública `anon` **no sustituye** a `DATABASE_URL` y no permite conectarse directamente al motor PostgreSQL. Se usa para solicitudes a la API REST de Supabase desde un cliente, junto con las políticas RLS adecuadas. Esa integración REST no está implementada en esta aplicación.

### 4.2 Cómo configurar las credenciales de forma segura

El Compose revisado contiene credenciales y un secreto de desarrollo directamente en el archivo. Antes de compartir el proyecto o publicarlo:

1. Rota la contraseña de PostgreSQL en Supabase si la conexión se compartió fuera de tu entorno.
2. Genera un `JWT_SECRET` largo y aleatorio.
3. Mueve `DATABASE_URL` y `JWT_SECRET` a un archivo de entorno local no versionado o a los secretos del entorno de despliegue.
4. Cambia Docker Compose para leer esos valores desde el entorno; no los escribas en README, capturas, código del frontend ni commits.
5. No uses el rol `service_role` ni la contraseña PostgreSQL en el navegador.

Los ejemplos de `backend/.env.example` son valores ilustrativos; no son credenciales de Supabase listas para usar. El Compose actual define la URL directamente, así que solo crear `.env` por sí solo no cambia la conexión hasta que Compose se modifique para leerlo.

### 4.3 Esquema y datos

Alembic prepara el esquema, pero no importa automáticamente un catálogo actualizado de propiedades. El dashboard lee los registros existentes mediante `GET /api/v1/properties`.

Para revisar desde Supabase si hay propiedades:

1. Abre el proyecto en Supabase → **SQL Editor** → **New query**.
2. Ejecuta:

   ```sql
   select count(*) from public.properties;
   ```

3. Un resultado mayor que cero confirma que esa tabla tiene filas. No confirma por sí solo que el esquema de las filas coincida con los modelos que consulta la API.

El script `backend/seed.py` contiene registros de demostración y crea/actualiza un usuario de prueba. No lo ejecutes contra una base de datos real o compartida sin revisar y adaptar el script: incluye una contraseña de prueba conocida y datos estáticos. Tampoco sustituye a una integración de ingesta real.

Una nota menciona que se ejecutó manualmente una consulta SQL en Supabase para corregir un problema, pero no identifica cuál era ni qué modificó. Antes de volver a ejecutar SQL manual, revisa el historial del SQL Editor y las migraciones de Alembic para evitar duplicar o contradecir ese cambio.

## 5. Cómo llegan los datos al dashboard

1. El usuario inicia sesión en la interfaz.
2. El frontend adjunta el JWT en `Authorization: Bearer ...`.
3. `web/src/hooks/useProperties.ts` solicita `/api/v1/properties`.
4. Vite reenvía la solicitud al backend local.
5. FastAPI valida el JWT y el endpoint consulta PostgreSQL mediante SQLAlchemy.
6. La respuesta paginada se muestra en el dashboard.

La ruta de propiedades requiere autenticación. En Swagger (`http://localhost:8000/docs`), expande `GET /api/v1/properties`, pulsa **Try it out** y **Execute**. Si la ruta responde `401`, falta una sesión o el token. La web debe tener una sesión válida para mostrar el dashboard.

## 6. Diagnóstico rápido

| Resultado | Qué significa / qué revisar |
|---|---|
| `GET /health` indica `"db":"up"` | El backend pudo ejecutar `SELECT 1` contra la base configurada. |
| `GET /api/v1/properties` devuelve `401` | Autoriza una sesión válida; la ruta está protegida. |
| Devuelve `200` con `items: []` | No hay resultados para los filtros aplicados o el conjunto consultado no contiene propiedades visibles al backend. Quita filtros y revisa las filas y esquema de `public.properties`. |
| Devuelve `500` | Revisa el error del backend y la coincidencia entre las tablas/columnas de Supabase y los modelos/migraciones. No compartas contraseñas ni la URL completa de conexión. |
| No abre el frontend | Confirma que `npm run dev` sigue activo y abre la dirección que indicó Vite. |
| Hay filas en Supabase, pero no aparecen en pantalla | Verifica conexión con `/health`, respuesta de la API, autorización y filtros del dashboard. |

Para ver logs del backend desde `backend`:

```powershell
docker compose logs api
```

## 7. Funciones implementadas y límites actuales

- Hay endpoints para autenticación, perfil, geografía, propiedades, guardados, cobertura, alertas, segmentos, exportación y administración.
- La vista de mapa usa Leaflet/OpenStreetMap. La interfaz incluye inglés, español, chino y alemán.
- Los proveedores de SMS, push y OAuth están configurados en modo `stub`; no se envía SMS ni push real y el OAuth real está pendiente.
- La ingesta está simulada: el servicio marca el trabajo como terminado, pero no descarga ni importa datos de una fuente externa.
- La exportación y los trabajos se ejecutan mediante tareas de fondo de FastAPI; Celery/Redis están presentes en Compose, pero la implementación indica que la cola de producción queda pendiente.
- La API de propiedades acepta un solo `county_id` por consulta; el frontend envía el primer condado seleccionado.
- Los datos de muestra no equivalen a datos reales o actualizados de remates. Verifica procedencia, fecha y exactitud antes de tomar decisiones.

## 8. Seguridad y preparación para producción

El código revisado contiene un problema crítico: el endpoint `POST /api/v1/auth/2fa/verify` emite tokens sin comprobar el código OTP, la expiración, los intentos ni el consumo del reto. No consideres la autenticación actual segura para cuentas reales hasta corregirlo.

Además:

- JWT conserva valores de demostración por defecto; configura un secreto seguro fuera del repositorio.
- El frontend guarda access y refresh tokens en `localStorage`; una vulnerabilidad XSS podría exponerlos.
- El rate limiting está en memoria y no coordina múltiples instancias.
- OAuth, SMS y push reales no están terminados.
- Las credenciales de base de datos que aparecían en Compose deben rotarse y retirarse del archivo.

Este README describe el MVP observado; no certifica que el sistema sea apto para producción. No se ejecutaron pruebas durante la preparación de esta guía.

## 9. Incidencias de pruebas reportadas en los archivos del proyecto

El archivo `Errores en pruebas.txt` reporta tres resultados:

1. Dos pruebas de registro esperaban `201 Created`, pero recibieron `200 OK`.
2. Una prueba esperaba que un código 2FA incorrecto recibiera `401 Unauthorized`, pero recibió `200 OK`.

Al revisar el código, el endpoint de registro no declara `status_code=201`, así que FastAPI devuelve `200` de forma predeterminada. El endpoint de verificación 2FA sí tiene un defecto funcional: emite tokens sin verificar el código OTP. Esto explica el segundo tipo de fallo y coincide con el problema de seguridad señalado arriba. Las pruebas no se volvieron a ejecutar para esta documentación.

La nota `Notas Adicionales.txt` también advierte que el entorno requiere la contraseña de Supabase configurada. La conexión depende de las credenciales PostgreSQL y de la conectividad de red; la clave pública `anon` no es esa contraseña.
