from pydantic import BaseModel
from app.schemas.base_schema import BaseMessageResponse


class LoginRequest(BaseModel):
    email: str
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
    

class MessageResponse(BaseMessageResponse):
    pass