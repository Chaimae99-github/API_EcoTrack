# app/models/indicator.py
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base

class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)

    type = Column(String, nullable=False)  # ex: "PM10", "CO2", "temperature"
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)  # "µg/m3", "ppm", "°C", etc.
    timestamp = Column(DateTime, nullable=False)

    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    extra_data  = Column(JSON, nullable=True)  # infos supplémentaires (optionnel)

    zone = relationship("Zone", back_populates="indicators")
    source = relationship("Source", back_populates="indicators")
