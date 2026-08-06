from sqlalchemy import Column, DateTime, String, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Pod(Base):
    __tablename__ = "pods"

    podID = Column(String, primary_key=True, index=True)
    podName = Column(String, nullable=False)
    deviceID = Column(String, ForeignKey("devices.deviceID"), nullable=False)
    plantID = Column(String, ForeignKey("plants.plantID"), nullable=True)
    
    plantAge = Column(Integer, nullable=True)
    plantCondition = Column(String, nullable=True)
    mode = Column(String, nullable=True)
    
    podPump = Column(Boolean, default=False)
    podLight = Column(Boolean, default=False)
    
    manualMoistureLevel = Column(Float, nullable=True)
    manualLightIntensity = Column(Float, nullable=True)
    defaultMoistureLevel = Column(Float, nullable=True)
    defaultLightIntensity = Column(Float, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    device = relationship("Device", back_populates="pod")
    plant = relationship("Plant", back_populates="pod")
    data_logs = relationship("PodDataLog", back_populates="pod")
    pod_logs = relationship("PodLog", back_populates="pod")
    systemLogs = relationship("SystemLog", back_populates="pod")