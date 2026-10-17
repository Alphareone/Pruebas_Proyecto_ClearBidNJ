# ClearBid NJ — Web (React + TypeScript)

Interfaz web de escritorio de la App de Oportunidades de Remate — New Jersey.
Consume el backend FastAPI (`../backend`). Replica el wireframe: autenticación
con 2FA, dashboard con vistas tabla/tarjetas/mapa, drawer de detalle con cuatro
pestañas (financiero, legal, físico, semáforo), guardadas, cobertura, alertas,
perfil, segmentos y exportación. Incluye modo oscuro e i18n en inglés, español,
chino y alemán.

## Stack

- **Vite** + **React 18** + **TypeScript** (SPA).
- **Tailwind CSS** con los tokens de diseño del wireframe (modo oscuro por clase).
- **TanStack Query** (fetching/cache) + **Axios** (interceptor con refresh JWT).
- **Zustand** (auth, tema, filtros, toasts).
- **React Router** (rutas protegidas).
- **react-i18next** (4 idiomas).
- **react-leaflet** + OpenStreetMap (vista de mapa, sin API key).

## Puesta en marcha

```bash
npm install
cp .env.example .env      # opcional: configura VITE_API_URL
npm run dev               # http://localhost:5173
```

En desarrollo, Vite hace proxy de `/api` y `/health` a `http://localhost:8000`
(el backend), así que no hace falta configurar CORS. Levanta el backend primero:

```bash
cd ../backend && docker compose up --build   # o uvicorn app.main:app --reload
```

Para producción:

```bash
npm run build     # genera dist/ (tsc -b && vite build)
npm run preview
```

Apunta `VITE_API_URL` al dominio real del backend (p. ej.
`https://api.clearbid-nj.com`) al compilar para producción.

## Flujo de autenticación

Login (email+contraseña) o OAuth → el backend responde con un reto 2FA →
pantalla de código de 6 dígitos → `2fa/verify` emite access+refresh token. El
access token se adjunta a cada request; ante un 401 el interceptor de Axios
renueva con el refresh token (rotación) y reintenta de forma transparente.

> **Modo stub:** el backend por defecto no envía SMS real; el código OTP aparece
> en su log (`[SMS-STUB]`). Los botones OAuth envían un token ficticio que el
> backend en modo stub acepta.

## Estructura

```
src/
  lib/         api (axios + refresh), tokens, format, queryClient
  types/       tipos TS de la API
  store/       zustand: auth, theme, filters, toast
  i18n/        configuración + locales (en/es/zh/de)
  hooks/       TanStack Query: properties, saved, segments, alerts, coverage, profile, export
  components/
    layout/    AppShell, TopBar, Sidebar
    properties/PropertyTable, PropertyCards, PropertyMap, SelectionBar, DetailDrawer
    auth/      AuthShell, OAuthButtons
    ui/        Chip, FlagPill, Toast, Spinner
  pages/       Login, TwoFactor, Dashboard, Saved, Alerts, Profile, Settings
  routes/      ProtectedRoute
```

## Notas

- El semáforo del backend (green/yellow/red) se mapea a las clases visuales del
  wireframe (g/a/r) en `lib/format.ts`.
- El listado del backend acepta un solo `county_id`; el filtro multi-county de la
  UI envía el primero seleccionado (para conjuntos usar segmentos/facetas).
- La exportación CSV se procesa como job asíncrono: la UI hace polling y abre la
  URL de descarga al completarse.
- Preferencias de idioma/tema se persisten localmente y se sincronizan con el
  backend (`/users/me/preferences`).
