from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.base_schema import BaseMessageResponse


class UserCreateRequest(BaseModel):
    email: str
    name: str
    password: str

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    password: Optional[str] = None

    def has_at_least_one_field(self):
        return any([self.name is not None, self.email is not None, self.password is not None])
    

class UserUpdateResponse(BaseModel):
    email: str
    name: str
    updated_at: datetime


class MessageResponse(BaseMessageResponse):
    pass
