import os

# Definir la estructura de carpetas y archivos con su contenido
structure = {
    "app": {
        "__init__.py": "",
        "database.py": '''from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./clearbid.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
''',
        "main.py": '''from fastapi import FastAPI
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
''',
        "models": {
            "__init__.py": "",
            "property.py": '''from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class PropertyModel(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True, nullable=False)
    county = Column(String, nullable=False)
    debt_amount = Column(Float, nullable=False)
    is_irs_lien = Column(Integer, default=0) # 1 = Sí, 0 = No
    risk_status = Column(String, nullable=False)  # Verde, Amarillo, Rojo
'''
        },
        "schemas": {
            "__init__.py": "",
            "property.py": '''from pydantic import BaseModel

class PropertyBase(BaseModel):
    address: str
    county: str
    debt_amount: float
    is_irs_lien: int

class PropertyCreate(PropertyBase):
    pass

class PropertyResponse(PropertyBase):
    id: int
    risk_status: str

    class Config:
        from_attributes = True
'''
        },
        "crud": {
            "__init__.py": "",
            "crud_property.py": '''from sqlalchemy.orm import Session
from app.models.property import PropertyModel
from app.schemas.property import PropertyCreate

def calculate_risk_status(debt: float, irs_lien: int) -> str:
    if irs_lien == 1 or debt > 50000:
        return "ROJO (Alto Riesgo - Deuda Crítica / IRS)"
    elif 15000 <= debt <= 50000:
        return "AMARILLO (Riesgo Moderado)"
    else:
        return "VERDE (Bajo Riesgo / Oportunidad viable)"

def get_properties(db: Session, skip: int = 0, limit: int = 10):
    return db.query(PropertyModel).offset(skip).limit(limit).all()

def create_property(db: Session, property_in: PropertyCreate):
    risk = calculate_risk_status(property_in.debt_amount, property_in.is_irs_lien)
    
    db_property = PropertyModel(
        address=property_in.address,
        county=property_in.county,
        debt_amount=property_in.debt_amount,
        is_irs_lien=property_in.is_irs_lien,
        risk_status=risk
    )
    db.add(db_property)
    db.commit()
    db.refresh(db_property)
    return db_property
'''
        },
        "api": {
            "__init__.py": "",
            "v1": {
                "__init__.py": "",
                "endpoints": {
                    "__init__.py": "",
                    "properties.py": '''from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.property import PropertyCreate, PropertyResponse
from app.crud import crud_property

router = APIRouter()

@router.get("/", response_model=List[PropertyResponse], summary="Listar propiedades evaluadas")
def read_properties(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    properties = crud_property.get_properties(db, skip=skip, limit=limit)
    return properties

@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED, summary="Registrar y evaluar una propiedad")
def create_property(property_in: PropertyCreate, db: Session = Depends(get_db)):
    return crud_property.create_property(db=db, property_in=property_in)
'''
                }
            }
        }
    },
    "tests": {
        "__init__.py": "",
        "test_properties.py": '''# Espacio reservado para pruebas con Pytest
def test_placeholder():
    assert True
'''
    },
    "requirements.txt": '''fastapi>=0.100.0
uvicorn>=0.22.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pytest>=7.0.0
requests>=2.31.0
''',
    "README.md": '''# ClearBid NJ - Backend MVP
Sistema de Inteligencia Pre-Puja para Remates Inmobiliarios en New Jersey.
'''
}

def create_structure(base_path, obj):
    for name, content in obj.items():
        current_path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(current_path, exist_ok=True)
            create_structure(current_path, content)
        else:
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Creado archivo: {current_path}")

if __name__ == "__main__":
    print("Construyendo estructura profesional del proyecto ClearBid NJ...")
    create_structure(".", structure)
    print("¡Proyecto generado con éxito! Ya puedes instalar dependencias e iniciar tu servidor.")