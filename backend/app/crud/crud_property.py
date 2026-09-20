from sqlalchemy.orm import Session
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
