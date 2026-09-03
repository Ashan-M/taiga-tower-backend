from pydantic import BaseModel, Field, model_validator
from typing import Optional, List

from app.mqtt.schemas import PodData


# class CreateLogSchema(BaseMod
class CreatePodDataLog(BaseModel):
    moistureLevel: Optional[float] = Field(None, ge=0.0, le=100.0)
    lightIntensity: Optional[float] = Field(None, ge=0.0, le=100.0)

class CreateSystemLog(BaseModel):
    message: str = Field(..., example="System log message")

class CreatePodsDataLog(BaseModel):
    deviceID: str
    pods: List[PodData]
