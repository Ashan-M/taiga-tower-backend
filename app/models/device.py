from sqlalchemy import Column, String, Boolean,DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone

class Device(Base):
    __tablename__ = "devices"

    deviceID = Column(String, primary_key=True, index=True)
    deviceType = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    masterLight = Column(Boolean, default=False)
    masterPump = Column(Boolean, default=False)
    floater = Column(Boolean, default=False)

    pod = relationship("Pod", back_populates="device")
    systemLogs = relationship("SystemLog", back_populates="device")
