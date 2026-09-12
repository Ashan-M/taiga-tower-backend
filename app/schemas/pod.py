from pydantic import BaseModel, Field, model_validator
from typing import Optional


class CreatePodSchema(BaseModel):

    podName: str = Field(..., example="POD 01")
    plantID: str = Field(..., example="PLANT_001")
    mode: str = Field(default="AUTO", pattern="^(AUTO|MANUAL)$")

    # Required ONLY if mode == "MANUAL"
    # pod_pump: Optional[bool] = False
    # pod_light: Optional[bool] = False
    # manual_moisture_level: Optional[float] = Field(None, ge=0.0, le=100.0)
    # manual_light_intensity: Optional[float] = Field(None, ge=0.0, le=100.0)

    @model_validator(mode="after")
    def validate_manual_fields(self):
        if self.mode == "MANUAL":
            missing_fields = []
            if self.manual_moisture_level is None:
                missing_fields.append("manual_moisture_level")
            if self.manual_light_intensity is None:
                missing_fields.append("manual_light_intensity")
            if self.pod_pump is None:
                missing_fields.append("pod_pump")
            if self.pod_light is None:
                missing_fields.append("pod_light")

            if missing_fields:
                raise ValueError(
                    f"When mode is 'MANUAL', the following fields are required: {', '.join(missing_fields)}"
                )
        return self

class PodDataLogs(BaseModel):
    podID: str
    timeStamp: str
    moistureLevel: float
    lightIntensity: float

class PodControlUpdate(BaseModel):
    podPump: Optional[bool] = None
    podLight: Optional[bool] = None
    manualLightIntensity: Optional[float] = Field(None, ge=0.0, le=100.0)
    manualMoistureLevel: Optional[float] = Field(None, ge=0.0, le=100.0)
    podPumpTimer: Optional[int] = Field(None, ge=0)  # Timer in seconds
