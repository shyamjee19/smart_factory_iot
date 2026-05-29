from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SensorDataResponse(BaseModel):
    id: int
    device_id: str
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    pressure: Optional[float] = None
    vibration: Optional[float] = None
    voltage: Optional[float] = None
    current: Optional[float] = None
    
    class Config:
        from_attributes = True

class SensorDataBulkResponse(BaseModel):
    items: List[SensorDataResponse]
    total: int

class TrendDataPoint(BaseModel):
    timestamp: datetime
    value: float
    device_id: str

class TrendResponse(BaseModel):
    data: List[TrendDataPoint]
    metric: str
