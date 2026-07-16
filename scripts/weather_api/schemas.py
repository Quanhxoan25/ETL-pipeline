from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class WeatherResponse(BaseModel):
    city_name: str
    country: str
    updated_time: datetime
    temperature: Optional[float]
    feels_like: Optional[float]
    humidity: Optional[int]
    condition: Optional[str]

    class Config:
        from_attributes = True