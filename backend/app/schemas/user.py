"""Schemas de usuarios y perfil (sección 5.2)."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Language, ORMModel, Role, Theme


class UserProfile(ORMModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    phone_verified: bool
    role: Role
    auth_providers: list[str] = []
    created_at: datetime


class UpdateProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = Field(None, description="Teléfono E.164")


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class VerifyPhoneRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class Preferences(BaseModel):
    language: Language = Language.en
    theme: Theme = Theme.system


class UpdatePreferencesRequest(BaseModel):
    language: Language | None = None
    theme: Theme | None = None
