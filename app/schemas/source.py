# app/schemas/source.py
from pydantic import BaseModel, HttpUrl

class SourceBase(BaseModel):
    name: str
    description: str | None = None
    url: HttpUrl | None = None
    type: str | None = None

class SourceCreate(SourceBase):
    pass

class SourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    url: HttpUrl | None = None
    type: str | None = None

class SourceRead(SourceBase):
    id: int

    class Config:
        from_attributes = True


