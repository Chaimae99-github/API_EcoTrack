# app/models/zone.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base

class Zone(Base):
    __tablename__ = "zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    postal_code = Column(String, nullable=True)

    # relation avec Indicator (une zone a plusieurs indicateurs)
    indicators = relationship("Indicator", back_populates="zone")

