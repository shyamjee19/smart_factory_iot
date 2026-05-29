from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.alert import Alert

def get_alerts(db: Session, skip: int = 0, limit: int = 100, severity: str = None, device_id: str = None, start_date=None, end_date=None):
    query = db.query(Alert)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    if device_id:
        query = query.filter(Alert.device_id == device_id)
    if start_date:
        query = query.filter(Alert.created_at >= start_date)
    if end_date:
        query = query.filter(Alert.created_at <= end_date)
        
    total = query.count()
    alerts = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()
    
    return {"items": alerts, "total": total}

def get_alert_stats(db: Session):
    critical = db.query(Alert).filter(Alert.severity == 'CRITICAL').count()
    warning = db.query(Alert).filter(Alert.severity == 'WARNING').count()
    info = db.query(Alert).filter(Alert.severity == 'INFO').count()
    unacknowledged = db.query(Alert).filter(Alert.is_acknowledged == False).count()
    
    return {
        "critical_count": critical,
        "warning_count": warning,
        "info_count": info,
        "unacknowledged_count": unacknowledged
    }

def acknowledge_alert(db: Session, alert_id: int, username: str):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
        
    from sqlalchemy.sql import func
    
    alert.is_acknowledged = True
    alert.acknowledged_by = username
    alert.acknowledged_at = func.now()
    
    db.commit()
    db.refresh(alert)
    return alert
