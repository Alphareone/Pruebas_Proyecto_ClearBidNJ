from fastapi import APIRouter, Depends, status
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
