from pydantic import BaseModel

class UserRegisterSchema(BaseModel):
    email: str
    name: str
    password: str

    class Config:
        from_attributes = True


class UserLoginSchema(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes = True