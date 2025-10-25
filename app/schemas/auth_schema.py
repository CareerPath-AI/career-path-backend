from pydantic import BaseModel

class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

    class Config:
        from_attributes = True


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
    

class MessageResponse(BaseModel):
    message: str
