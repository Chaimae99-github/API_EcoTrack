# app/schemas/indicator.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel

class IndicatorBase(BaseModel):
    type: str
    value: float
    unit: str
    timestamp: datetime
    zone_id: int
    source_id: int
    extra_data: dict[str, Any] | None = None

class IndicatorCreate(IndicatorBase):
    pass

class IndicatorUpdate(BaseModel):
    type: str | None = None
    value: float | None = None
    unit: str | None = None
    timestamp: datetime | None = None
    zone_id: int | None = None
    source_id: int | None = None
    extra_data: dict[str, Any] | None = None

class IndicatorRead(IndicatorBase):
    id: int

    class Config:
        from_attributes = True


