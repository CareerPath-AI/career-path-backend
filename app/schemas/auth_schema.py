from pydantic import BaseModel, EmailStr
from app.schemas.base_schema import BaseMessageResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str


class MessageResponse(BaseMessageResponse):
    pass