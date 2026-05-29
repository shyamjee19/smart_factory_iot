from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime, date

class DeviceHealthBase(BaseModel):
    uptime_percentage: float
    anomaly_count: int
    health_score: float
    last_seen: Optional[datetime]
    
    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    location: Optional[str] = None
    install_date: Optional[date] = None
    status: str
    metadata_: Optional[Any] = None

class DeviceResponse(DeviceBase):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DeviceDetailResponse(DeviceResponse):
    health: Optional[DeviceHealthBase] = None
    latest_reading: Optional[Any] = None # Will be populated with SensorDataResponse

class DeviceListResponse(BaseModel):
    items: List[DeviceResponse]
    total: int
