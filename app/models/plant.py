from sqlalchemy import Column, String, Integer, Float, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Plant(Base):
    __tablename__ = "plants"

    plantID = Column(String, primary_key=True, index=True)
    plantName = Column(String, nullable=False)
    maxGrowthPeriod = Column(Integer, nullable=True)
    moistureLevel = Column(Float, nullable=True)
    lightIntensity = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # MUST match back_populates="plant" in the Pod model
    pod = relationship("Pod", back_populates="plant")

