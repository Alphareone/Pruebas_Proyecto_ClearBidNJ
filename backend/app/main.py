from fastapi import FastAPI
from app.database import engine, Base
from app.api.v1.endpoints import properties

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ClearBid NJ API",
    description="Backend oficial para el motor de inteligencia y análisis de remates inmobiliarios.",
    version="1.0.0"
)

app.include_router(properties.router, prefix="/api/v1/properties", tags=["Propiedades y Riesgo"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenido a ClearBid NJ API - Sistema Operativo"}
