from pydantic import BaseModel

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
