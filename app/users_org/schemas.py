# app/users_org/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from .models import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    department_id: Optional[int] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True
