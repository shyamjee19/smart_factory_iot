from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.alert import AlertListResponse, AlertStats, AlertResponse, AlertAcknowledge
from app.services import alert_service
from app.services.auth_service import get_current_user, role_required
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=AlertListResponse)
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    severity: Optional[str] = None,
    device_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all alerts with optional filtering."""
    return alert_service.get_alerts(
        db, skip=skip, limit=limit, severity=severity, 
        device_id=device_id, start_date=start_date, end_date=end_date
    )

@router.get("/stats", response_model=AlertStats)
def get_alert_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary statistics of alerts."""
    return alert_service.get_alert_stats(db)

@router.put("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    ack_data: AlertAcknowledge,
    db: Session = Depends(get_db),
    # Only Admin or Operator can acknowledge alerts
    current_user: User = Depends(role_required(["admin", "operator"])) 
):
    """Acknowledge an alert (requires Admin or Operator role)."""
    alert = alert_service.acknowledge_alert(db, alert_id, current_user.username)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
