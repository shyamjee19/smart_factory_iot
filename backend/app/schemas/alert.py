from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AlertBase(BaseModel):
    device_id: str
    alert_type: str
    severity: str
    metric: str
    threshold_value: float
    actual_value: float
    message: str

class AlertResponse(AlertBase):
    id: int
    is_acknowledged: bool
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class AlertListResponse(BaseModel):
    items: List[AlertResponse]
    total: int

class AlertAcknowledge(BaseModel):
    is_acknowledged: bool = True

class AlertStats(BaseModel):
    critical_count: int
    warning_count: int
    info_count: int
    unacknowledged_count: int
