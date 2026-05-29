from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.device import DeviceMaster, DeviceHealth
from app.models.sensor_data import SensorData

def get_all_devices(db: Session, skip: int = 0, limit: int = 100, device_type: str = None, status: str = None):
    query = db.query(DeviceMaster)
    
    if device_type:
        query = query.filter(DeviceMaster.device_type == device_type)
    if status:
        query = query.filter(DeviceMaster.status == status)
        
    total = query.count()
    devices = query.order_by(DeviceMaster.device_name).offset(skip).limit(limit).all()
    
    return {"items": devices, "total": total}

def get_device_by_id(db: Session, device_id: str):
    device = db.query(DeviceMaster).filter(DeviceMaster.device_id == device_id).first()
    if not device:
        return None
        
    # Get latest reading
    latest_reading = db.query(SensorData).filter(
        SensorData.device_id == device_id
    ).order_by(desc(SensorData.timestamp)).first()
    
    # We construct a response dict that matches the DeviceDetailResponse schema
    result = {
        "device_id": device.device_id,
        "device_name": device.device_name,
        "device_type": device.device_type,
        "location": device.location,
        "install_date": device.install_date,
        "status": device.status,
        "metadata_": device.metadata_,
        "created_at": device.created_at,
        "updated_at": device.updated_at,
        "health": device.health,
        "latest_reading": latest_reading
    }
    
    return result

def get_device_readings(db: Session, device_id: str, start_date=None, end_date=None, skip: int = 0, limit: int = 100):
    query = db.query(SensorData).filter(SensorData.device_id == device_id)
    
    if start_date:
        query = query.filter(SensorData.timestamp >= start_date)
    if end_date:
        query = query.filter(SensorData.timestamp <= end_date)
        
    total = query.count()
    readings = query.order_by(desc(SensorData.timestamp)).offset(skip).limit(limit).all()
    
    return {"items": readings, "total": total}
