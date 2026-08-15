from typing import Optional
from pydantic import BaseModel

class DeviceActivateMessage(BaseModel):
    messageID: str
    deviceID: str

class ActivatePodMessage(BaseModel):
    messageID: str
    deviceID: str
    podID: str
    mode: str
    plantID: str
    defaultMoistureLevel: float
    defaultLightIntensity: float
    manualMoistureLevel: Optional[float] = None
    manualLightIntensity: Optional[float] = None

class DeviceCommandMessage(BaseModel):
    messageID: str
    deviceID: str
    masterLight: Optional[bool] = None
    masterPump: Optional[bool] = None

class PodCommandMessage(BaseModel):
    messageID: str
    deviceID: str
    podID: str
    podPump: Optional[bool] = None
    podLight: Optional[bool] = None
    manualMoistureLevel: Optional[float] = None
    manualLightIntensity: Optional[float] = None

class PodData(BaseModel):
    podID: str
    moistureLevel: float
    lightIntensity: float

class DeviceDataMessage(BaseModel):
    messageID: str
    deviceID: str
    timestamp: str
    pods: list[PodData]

class MQTTAck(BaseModel):
    messageID: str
    deviceID: str
    status: str
    podID: Optional[str] = None
    error: Optional[str] = None