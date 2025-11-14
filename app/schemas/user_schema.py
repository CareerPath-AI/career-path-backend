from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.base_schema import BaseMessageResponse


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None

    def has_at_least_one_field(self):
        return any([self.name is not None, self.email is not None, self.password is not None])
    

class UserUpdateResponse(BaseModel):
    email: EmailStr
    name: str
    updated_at: datetime


class UserDeleteRequest(BaseModel):
    password: str


class UserGetResponse(BaseModel):
    email: EmailStr
    name: str
    created_at: datetime


class MessageResponse(BaseMessageResponse):
    pass
