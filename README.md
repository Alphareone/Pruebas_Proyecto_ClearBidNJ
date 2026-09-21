
# 🏡 ClearBid NJ - Sistema de Inteligencia Pre-Puja de Remates en New Jersey (SIPPRI)

Plataforma inteligente de análisis y evaluación de riesgos para remates judiciales inmobiliarios (*Sheriff Sales*) en het estado de New Jersey. El objetivo del sistema es procesar variables críticas de deuda y gravámenes para emitir un semáforo de riesgo automatizado antes de la inversión.

---

## 🛑 INSTRUCCIONES CLAVE: CÓMO TRABAJAR EN TU RAMA ASIGNADA

Para evitar conflictos de código, **ninguno debe trabajar directamente sobre la rama `main`**. Cada integrante tiene una rama exclusiva según su rol. Sigue estos pasos en tu terminal para posicionarte en tu espacio de trabajo:

1. Clona el repositorio (si aún no lo tienes):
   ```bash
   git clone [https://github.com/Alphareone/Pruebas_Proyecto_ClearBidNJ.git](https://github.com/Alphareone/Pruebas_Proyecto_ClearBidNJ.git)
   cd Pruebas_Proyecto_ClearBidNJ

```

2. Actualiza los cambios generales:
```bash
git pull origin main

```


3. **Cambiate a la rama correspondiente a tu rol** (ejecuta el comando exacto que te toca):
* **Alfredo (Backend):** `git checkout feature/backend`
* **Cris (Frontend):** `git checkout feature/frontend`
* **Felipe (Database):** `git checkout feature/data-engine`
* **Matías (QA & Docs):** `git checkout feature/devops-qa`


4. Cada vez que termines una tarea o vayas a avanzar, sube tus cambios únicamente a tu rama:
```bash
git add .
git commit -m "feat: [tu descripción del avance]"
git push origin [nombre-de-tu-rama]

```



---

## 🚀 Guía de Configuración y Ejecución Paso a Paso

### 1. Cómo Levantar el Backend (FastAPI)

1. Entra a la carpeta del backend:
```bash
cd backend

```


2. Crear y activar el entorno virtual:
* **En Windows (PowerShell):**
```bash
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

```


* **En Mac / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate

```




3. Instalar las dependencias:
```bash
pip install -r requirements.txt

```


4. Ejecutar el Servidor de Desarrollo:
```bash
uvicorn app.main:app --reload

```



*✨ El servidor correrá en `http://127.0.0.1:8000`. Documentación interactiva en:* 👉 **`http://127.0.0.1:8000/docs`**

---

### 2. Cómo Levantar el Frontend (React + Vite)

1. Abre **otra pestaña de tu terminal** y entra a la carpeta del frontend:
```bash
cd frontend

```


2. Instala las dependencias de Node.js:
```bash
npm install

```


3. Inicia el servidor de desarrollo visual:
```bash
npm run dev

```



*✨ La interfaz web estará disponible en `http://localhost:5173`.*

---

## 👥 Asignación Oficial de Roles y Responsabilidades - Fase 2

* **🔒 Alfredo (Backend & Security)**
* Lógica de la API en FastAPI, rutas, autenticación y seguridad del servidor (`backend/app/`).
* Rama de trabajo: `feature/backend`


* **💻 Cris (Frontend - React + Vite)**
* Desarrollo de la interfaz de usuario, pantallas del panel (*Dashboard*) y componentes visuales (`frontend/src/`).
* Rama de trabajo: `feature/frontend`


* **🗄️ Felipe (Database)**
* Gestión de la base de datos relacional, modelos de SQLAlchemy y migraciones.
* Rama de trabajo: `feature/data-engine`


* **📋 Matías (QA, Documentación y Drive)**
* Ejecución de pruebas de calidad y automatizadas (`pytest`) en la carpeta `tests/`.
* Organización de evidencias en Google Drive y control de documentación.
* Rama de trabajo: `feature/devops-qa`



---

## 📂 Estructura Completa del Repositorio

```text
Pruebas_Proyecto_ClearBidNJ/
│
├── backend/                              # Lógica y API (FastAPI)
│   ├── app/                              # Endpoints, modelos, schemas y crud
│   ├── tests/                            # Pruebas automatizadas (Pytest)
│   └── requirements.txt                  # Dependencias Python
│
├── frontend/                             # Interfaz Visual (React + Vite)
│   ├── src/                              # Componentes y vistas
│   ├── package.json                      # Dependencias Node.js
│   └── vite.config.js                    # Configuración de Vite
│
├── .gitignore                            # Archivos excluidos (ej. .venv, node_modules)
└── README.md                             # Documentación del equipo

```

---

## 📋 Protocolo de Evidencias y Comunicación

1. **Trabaja estrictamente en tu rama** asignada y no toques las de tus compañeros.
2. **Comparte tus avances** con capturas o videos cortos en el **grupo de WhatsApp**.
3. **Guarda respaldos** subiendo las evidencias requeridas a la carpeta compartida de **Google Drive**.

```

```
