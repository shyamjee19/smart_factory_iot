from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.database import get_db
from app.schemas.sensor_data import TrendResponse
from app.services import analytics_service
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get high-level dashboard metrics."""
    return analytics_service.get_dashboard_summary(db)

@router.get("/temperature-trend", response_model=TrendResponse)
def get_temperature_trend(
    range: str = Query("24h", regex="^(1h|6h|24h|7d)$"),
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated temperature data over time."""
    return analytics_service.get_trend_data(db, "temperature", range, device_id)

@router.get("/vibration-trend", response_model=TrendResponse)
def get_vibration_trend(
    range: str = Query("24h", regex="^(1h|6h|24h|7d)$"),
    device_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated vibration data over time."""
    return analytics_service.get_trend_data(db, "vibration", range, device_id)

@router.get("/device-health")
def get_device_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get health scores for all devices."""
    return analytics_service.get_device_health_summary(db)

@router.get("/export")
def export_data(
    format: str = Query("csv", regex="^(csv|xlsx)$"),
    metric: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export sensor data to CSV or Excel."""
    content, media_type = analytics_service.export_data(db, format, metric, start_date, end_date)
    
    if not content:
        return {"error": "Failed to generate export"}
        
    filename = f"factory_data_export_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.{format}"
    
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
