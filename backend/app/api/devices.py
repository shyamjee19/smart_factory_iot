from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.device import DeviceListResponse, DeviceDetailResponse
from app.schemas.sensor_data import SensorDataBulkResponse
from app.services import device_service
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=DeviceListResponse)
def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all devices with optional filtering."""
    return device_service.get_all_devices(db, skip=skip, limit=limit, device_type=type, status=status)

@router.get("/{device_id}", response_model=DeviceDetailResponse)
def get_device_detail(
    device_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details for a specific device, including health and latest reading."""
    device = device_service.get_device_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.get("/{device_id}/readings", response_model=SensorDataBulkResponse)
def get_device_readings(
    device_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get historical sensor readings for a specific device."""
    return device_service.get_device_readings(
        db, device_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit
    )
