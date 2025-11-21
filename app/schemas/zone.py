# app/schemas/zone.py
from pydantic import BaseModel

class ZoneBase(BaseModel):
    name: str
    postal_code: str | None = None

class ZoneCreate(ZoneBase):
    pass

class ZoneUpdate(BaseModel):
    name: str | None = None
    postal_code: str | None = None

class ZoneRead(ZoneBase):
    id: int

    class Config:
        from_attributes = True
