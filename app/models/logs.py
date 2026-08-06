from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime, timezone

class PodDataLog(Base):
    __tablename__ = "podDataLog"

    id = Column(Integer, primary_key=True, autoincrement=True)  # Composite or surrogate PK
    podID = Column(String, ForeignKey("pods.podID"), nullable=False)
    timeStamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    moistureLevel = Column(Float, nullable=True)
    lightIntensity = Column(Float, nullable=True)

    # Relationships
    pod = relationship("Pod", back_populates="data_logs")


class PodLog(Base):
    __tablename__ = "podLogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    podID = Column(String, ForeignKey("pods.podID"), nullable=False)
    deviceID = Column(String, ForeignKey("devices.deviceID"), nullable=False)
    timeStamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    pod = relationship("Pod", back_populates="pod_logs")


class SystemLog(Base):
    __tablename__ = "systemLogs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    deviceID = Column(String, ForeignKey("devices.deviceID"), nullable=False)
    podID = Column(String, ForeignKey("pods.podID"), nullable=True)
    timeStamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    message = Column(String, nullable=False)
    # Relationships
    device = relationship("Device", back_populates="systemLogs")
    pod = relationship("Pod", back_populates="systemLogs")