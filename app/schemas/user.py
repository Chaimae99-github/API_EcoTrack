# app/schemas/user.py
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    role: str = "user"

class UserCreate(UserBase):
    password: str  # mot de passe en clair côté API, on le hash avant de stocker

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    is_active: bool | None = None
    role: str | None = None

class UserRead(UserBase):
    id: int

    class Config:
        from_attributes = True  # Pydantic v2 (ou orm_mode=True en v1)



