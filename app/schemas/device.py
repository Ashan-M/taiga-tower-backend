from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class DeviceTypeEnum(str, Enum):
    TAIGA_TOWER = "Taiga Tower"
    TAIGA_LITE = "Taiga Lite"
    CAMERA_EXTENSION = "Camera Extension"

class CreateDeviceSchema(BaseModel):
    device_type: DeviceTypeEnum = Field(
        ..., 
        description="Select the type of device",
        example="Taiga Tower"
    )

class DeviceMasterControl(BaseModel):
    masterLight: Optional[bool] = None
    masterPump: Optional[bool] = None
    sleepMode: Optional[bool] = None