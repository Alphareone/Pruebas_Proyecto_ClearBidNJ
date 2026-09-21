
# 🏡 ClearBid NJ - Sistema de Inteligencia Pre-Puja de Renates en New Jersey (SIPP-RNJ)

Plataforma inteligente de análisis y evaluación de riesgos para remates judiciales inmobiliarios (*Sheriff Sales*) en el estado de New Jersey. El objetivo del sistema es procesar variables críticas de deuda y gravámenes federales para emitir un semáforo de riesgo automatizado antes de la inversión.

---

## 🛠️ Estado Actual del Proyecto (Fase 2: Arquitectura e Implementación)
Actualmente contamos con el **Núcleo Funcional (MVP) del Backend** implementado bajo una arquitectura modular limpia (Clean Architecture), con persistencia en base-de-datos y un motor de reglas operativo.

---

## 🚀 Instrucciones de Configuración y Ejecución (Backend)

Sigue estos pasos en tu terminal para levantar el entorno de desarrollo local:

### 1. Clonar el repositorio y entrar al directorio
```bash
git clone [https://github.com/Alphareone/Pruebas_Proyecto_ClearBidNJ.git](https://github.com/Alphareone/Pruebas_Proyecto_ClearBidNJ.git)
cd Pruebas_Proyecto_ClearBidNJ

```

### 2. Crear y activar el entorno virtual

* **En Windows (PowerShell):**
```bash
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\venv\Scripts\Activate.ps1

```


* **En Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate

```



### 3. Instalar las dependencias

```bash
pip install -r requirements.txt

```

### 4. Ejecutar el Servidor de Desarrollo

```bash
uvicorn app.main:app --reload

```

Una vez iniciado, el servidor correrá en `http://127.0.0.1:8000`. Puedes acceder a la documentación interactiva de la API (Swagger UI) en:
👉 **`http://127.0.0.1:8000/docs`**

---

## 👥 Plan de Trabajo y Asignación de Tareas - Fase 2

Debido al retraso inicial y la necesidad de acelerar la integración horizontal, el equipo se dividirá las siguientes responsabilidades críticas para los próximos días:

### 📋 Integrante 1: Backend y Datos (En curso / Refinamiento)

* **Objetivo:** Ampliar los endpoints y refinar el motor de reglas.
* **Tareas:**
* Agregar nuevos campos al modelo de propiedades (ej. fecha de subasta, tasación base, condado específico de NJ).
* Crear filtros avanzados de búsqueda por gravámenes del IRS y umbrales de deuda.
* Documentar los modelos de datos para la sincronización con el frontend.



### 💻 Integrante 2: Frontend y Consumo de API (React + Vite)

* **Objetivo:** Desarrollar la interfaz gráfica de usuario conectada al backend.
* **Tareas:**
* Configurar la estructura base del Frontend con React y Vite.
* Diseñar la vista principal del panel de control (*Dashboard*) con indicadores visuales del semáforo de riesgo (Verde, Amarillo, Rojo).
* Implementar el formulario de registro de propiedades que consuma directamente el endpoint `POST /api/v1/properties/` de FastAPI.



### 🧪 Integrante 3: QA, Pruebas y Documentación (Capstones)

* **Objetivo:** Garantizar la calidad del software y cumplir con la pauta académica.
* **Tareas:**
* Escribir pruebas unitarias e integración en la carpeta `tests/` usando `Pytest`.
* Consolidar las evidencias técnicas y redactar las conclusiones para el **Informe de Avance (Fase 2)** y el **Diario de Reflexión**.
* Monitorear la integración continua en el repositorio de GitHub.



---

## 📂 Estructura del Repositorio

```text
├── app/                      # Código fuente principal (FastAPI)
│   ├── api/v1/endpoints/     # Rutas y controladores HTTP
│   ├── crud/                 # Lógica de acceso a datos
│   ├── models/               # Modelos de Base de Datos (SQLAlchemy)
│   ├── schemas/              # Validación de esquemas (Pydantic)
│   ├── database.py           # Conexión y sesión de BD
│   └── main.py               # Punto de entrada de la aplicación
├── tests/                    # Pruebas automatizadas (Pytest)
├── requirements.txt          # Dependencias del proyecto
└── README.md                 # Documentación técnica

```

```

---

### ¿Cómo subir este archivo a GitHub rápidamente?

1. Ve a tu proyecto en Visual Studio Code.
2. Abre o reemplaza el contenido del archivo `README.md` que está en la raíz con el texto de arriba.
3. Guarda los cambios (`Ctrl + S`).
4. Ejecuta estos comandos en tu terminal para actualizar el repositorio:
   ```powershell
   git add README.md
   git commit -m "docs: update README with setup instructions and Phase 2 task breakdown"
   git push origin main

