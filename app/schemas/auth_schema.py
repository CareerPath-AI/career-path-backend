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