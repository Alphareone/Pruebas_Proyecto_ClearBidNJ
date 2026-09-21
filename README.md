
# 🏡 ClearBid NJ - Sistema de Inteligencia Pre-Puja de Remates en New Jersey (SIPPRI)

Plataforma inteligente de análisis y evaluación de riesgos para remates judiciales inmobiliarios (*Sheriff Sales*) en el estado de New Jersey. El objetivo del sistema es procesar variables críticas de deuda y gravámenes para emitir un semáforo de riesgo automatizado antes de la inversión.

---

## 🛠️ Estado Actual del Proyecto (Fase 2: Arquitectura e Implementación en Paralelo)
Actualmente contamos con el **Núcleo Funcional (MVP) del Backend** implementado en una estructura modular limpia, con persistencia en base de datos y un motor de reglas operativo. 

Para trabajar en equipo de forma ordenada sin pisarnos el código, hemos distribuido el proyecto en un formato **monorepo** y utilizado **ramas independientes por rol**.

---

## 🌿 Estrategia de Ramas por Rol en Git
Antes de empezar a programar, asegúrate de cambiarte a la rama correspondiente a tu rol:
* **`main`**: Rama estable oficial.
* **`feature/backend`**: Exclusiva para la lógica de la API y rutas (`backend/app/`).
* **`feature/frontend`**: Exclusiva para la interfaz visual en React (`frontend/src/`).
* **`feature/data-engine`**: Enfocada en modelos de base de datos, ORM y motor de riesgo.
* **`feature/devops-qa`**: Enfocada en pruebas automáticas (`tests/`) y validación de calidad.

Para moverte a tu rama, ejecuta en tu terminal:
```bash
git checkout tu-rama-asignada

```

---

## 🚀 Guía de Configuración y Ejecución Paso a Paso

### 1. Clonar el repositorio y entrar al directorio

```bash
git clone [https://github.com/Alphareone/Pruebas_Proyecto_ClearBidNJ.git](https://github.com/Alphareone/Pruebas_Proyecto_ClearBidNJ.git)
cd Pruebas_Proyecto_ClearBidNJ

```

---

### 2. Cómo Levantar el Backend (FastAPI)

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



*✨ El servidor correrá en `http://127.0.0.1:8000`. Puedes probar la API interactivamente en:* 👉 **`http://127.0.0.1:8000/docs`**

---

### 3. Cómo Levantar el Frontend (React + Vite)

1. Abre **otra pestaña o ventana de tu terminal** y entra a la carpeta del frontend:
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



*✨ La interfaz web estará disponible en el puerto local indicado en pantalla (usualmente `http://localhost:5173`).*

---

## 👥 Plan de Trabajo y Asignación de Tareas - Fase 2

Debido al retraso inicial y la necesidad de acelerar el desarrollo, cada integrante avanzará en paralelo sobre su módulo correspondiente:

### 🧠 Backend & Security (Alfredo)

* Ampliar y refinar los endpoints de FastAPI.
* Agregar campos al modelo de propiedades (fecha de subasta, tasación, condados de NJ).
* Consolidar los contratos de datos (JSON) para la comunicación con el frontend.

### 💻 Frontend Lead (Cristopher)

* Configurar la estructura base de React con Vite y componentes visuales.
* Diseñar el panel de control (*Dashboard*) con indicadores del semáforo de riesgo (Verde, Amarillo, Rojo).
* Conectar los formularios de la interfaz con los endpoints de la API (`POST /api/v1/properties/`).

### 🗄️ Database & Data Engine (Felipe)

* Estructurar migraciones limpias y robustas con SQLAlchemy.
* Alimentar la base de datos local con un set inicial de propiedades de prueba en New Jersey.
* Perfeccionar las reglas lógicas del motor de evaluación de riesgos.

### 🧪 DevOps, QA & Async Services (Matías)

* Escribir pruebas unitarias e de integración en la carpeta `tests/` usando `Pytest`.
* Validar que la guía de instalación del `README.md` funcione sin errores para todo el equipo.
* Consolidar evidencias técnicas para el Google Drive y apoyar en el control de calidad.

---

## 📂 Estructura Completa del Repositorio

```text
Pruebas_Proyecto_ClearBidNJ/
│
├── backend/                              # 🧠 Rama: feature/backend (FastAPI & Lógica)
│   ├── app/                              # Código fuente principal del backend
│   │   ├── api/                          # Endpoints y rutas HTTP (v1)
│   │   ├── crud/                         # Lógica de acceso e interacción con la BD
│   │   ├── models/                       # Modelos de Base de Datos (SQLAlchemy)
│   │   ├── schemas/                      # Esquemas de validación de datos (Pydantic)
│   │   ├── database.py                   # Configuración de conexión y sesión de BD
│   │   └── main.py                       # Punto de entrada principal de la API
│   ├── tests/                            # Pruebas automatizadas (Pytest)
│   └── requirements.txt                  # Dependencias de Python del proyecto
│
├── frontend/                             # 💻 Rama: feature/frontend (React & UI)
│   ├── src/                              # Componentes, vistas y lógica visual
│   ├── public/                           # Archivos estáticos e imágenes
│   ├── package.json                      # Dependencias de Node.js / React
│   └── vite.config.js                    # Configuración de Vite / entorno de desarrollo
│
├── .gitignore                            # Archivos excluidos de Git (ej. .venv, node_modules)
└── README.md                             # Esta documentación técnica del equipo

```

---

## 📋 Protocolo de Evidencias y Comunicación

1. **Trabaja en tu rama:** Haz commits limpios y descriptivos en tu rama asignada.
2. **Comparte avances:** Publica tus capturas o avances en el **grupo de WhatsApp** del equipo.
3. **Guarda respaldos:** Sube las evidencias requeridas a la carpeta compartida de **Google Drive**.

```

### ¿Cómo actualizarlo en tu repositorio?
1. Copia todo este código en formato Markdown.
2. Reemplaza el contenido del archivo `README.md` en la raíz de tu proyecto en Visual Studio Code.
3. Guarda los cambios y súbelo a GitHub con estos comandos en tu terminal:
   ```bash
   git add README.md
   git commit -m "docs: comprehensive update of README with separated backend/frontend instructions and role breakdown"
   git push origin main

```
