"""Schemas de autenticación y 2FA (sección 5.1)."""
from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Role


class RegisterRequest(BaseModel):
    first_name: str = Field(..., examples=["Max"])
    last_name: str = Field(..., examples=["Weller"])
    email: EmailStr = Field(..., examples=["max@wellq.co.uk"])
    phone: str = Field(..., description="Teléfono en formato E.164", examples=["+12015550199"])
    password: str = Field(..., min_length=8, examples=["S3cret!pass"])


class RegisterResponse(BaseModel):
    user_id: str
    challenge_id: str
    method: str = "sms"
    masked_phone: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChallengeResponse(BaseModel):
    challenge_id: str
    method: str = "sms"
    masked_phone: str | None = None


class OAuthRequest(BaseModel):
    id_token: str = Field(
        ..., description="id_token (Google/Apple) o access_token (Facebook)."
    )


class OAuthResponse(BaseModel):
    status: str = "2fa_required"
    challenge_id: str
    masked_phone: str | None = None


class Send2FARequest(BaseModel):
    challenge_id: str


class Send2FAResponse(BaseModel):
    sent: bool = True
    expires_in: int


class Verify2FARequest(BaseModel):
    challenge_id: str
    code: str = Field(..., min_length=6, max_length=6, examples=["481932"])


class UserPublic(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    role: Role


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserPublic | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
