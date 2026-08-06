from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class CreatePlantSchema(BaseModel):
    # plantID: str = Field(..., example="PLANT_001")
    plantName: str = Field(..., example="Tomato")
    maxGrowthPeriod: Optional[int] = None
    moistureLevel: Optional[float] = Field(None, ge=0.0, le=100.0)
    lightIntensity: Optional[float] = Field(None, ge=0.0, le=100.0)

    
