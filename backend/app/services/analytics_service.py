from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from app.models.device import DeviceMaster, DeviceHealth
from app.models.alert import Alert
from app.models.sensor_data import SensorData
import pandas as pd
import io

def get_dashboard_summary(db: Session):
    total_devices = db.query(DeviceMaster).count()
    online_devices = db.query(DeviceMaster).filter(DeviceMaster.status == 'online').count()
    offline_devices = db.query(DeviceMaster).filter(DeviceMaster.status == 'offline').count()
    
    # Alerts in last 24h
    recent_alerts = db.query(Alert).filter(Alert.created_at >= datetime.utcnow() - timedelta(days=1)).count()
    
    # Avg health score
    avg_health = db.query(func.avg(DeviceHealth.health_score)).scalar()
    
    return {
        "total_devices": total_devices,
        "online_devices": online_devices,
        "offline_devices": offline_devices,
        "alerts_24h": recent_alerts,
        "average_health_score": round(float(avg_health or 0), 2)
    }

def get_trend_data(db: Session, metric_col, time_range: str, device_id: str = None):
    # Determine time filter
    now = datetime.utcnow()
    if time_range == "1h":
        start_time = now - timedelta(hours=1)
        interval = "1 minute"
    elif time_range == "6h":
        start_time = now - timedelta(hours=6)
        interval = "5 minutes"
    elif time_range == "24h":
        start_time = now - timedelta(hours=24)
        interval = "15 minutes"
    else: # 7d default
        start_time = now - timedelta(days=7)
        interval = "1 hour"

    # PostgreSQL time_bucket or date_trunc equivalent to downsample data
    # For simplicity, we'll use date_trunc for this demo, though time_bucket (TimescaleDB) is better
    if interval.endswith("minute") or interval.endswith("minutes"):
        trunc = "minute"
    else:
        trunc = "hour"

    # Building raw SQL for complex aggregation
    query_str = f"""
        SELECT 
            date_trunc('{trunc}', timestamp) as bucket,
            device_id,
            AVG({metric_col}) as avg_val
        FROM sensor_data
        WHERE timestamp >= :start_time
    """
    params = {"start_time": start_time}
    
    if device_id:
        query_str += " AND device_id = :device_id"
        params["device_id"] = device_id
        
    query_str += " GROUP BY bucket, device_id ORDER BY bucket"
    
    result = db.execute(text(query_str), params)
    
    data = []
    for row in result:
        data.append({
            "timestamp": row.bucket,
            "device_id": row.device_id,
            "value": float(row.avg_val) if row.avg_val else 0.0
        })
        
    return {"data": data, "metric": metric_col}

def get_device_health_summary(db: Session):
    health_records = db.query(DeviceHealth).all()
    # Could join with DeviceMaster for names
    return [{"device_id": h.device_id, "score": float(h.health_score)} for h in health_records]

def export_data(db: Session, format: str, metric: str = None, start_date=None, end_date=None):
    # Simplified export logic using Pandas
    query = db.query(SensorData)
    if start_date: query = query.filter(SensorData.timestamp >= start_date)
    if end_date: query = query.filter(SensorData.timestamp <= end_date)
    
    # Limit for demo purposes
    data = query.limit(10000).all()
    
    # Convert to list of dicts
    dict_data = []
    for d in data:
        row = {"timestamp": d.timestamp, "device_id": d.device_id}
        if metric == "temperature" or not metric: row["temperature"] = d.temperature
        if metric == "vibration" or not metric: row["vibration"] = d.vibration
        # ... add other metrics
        dict_data.append(row)
        
    df = pd.DataFrame(dict_data)
    
    if format == 'csv':
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue(), "text/csv"
    elif format == 'xlsx':
        output = io.BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    
    return None, None
