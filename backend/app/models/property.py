from sqlalchemy import Column, Integer, String, Float
from app.database import Base

class PropertyModel(Base):
    __tablename__ = "properties"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True, nullable=False)
    county = Column(String, nullable=False)
    debt_amount = Column(Float, nullable=False)
    is_irs_lien = Column(Integer, default=0) # 1 = Sí, 0 = No
    risk_status = Column(String, nullable=False)  # Verde, Amarillo, Rojo
