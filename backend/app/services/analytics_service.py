from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from datetime import datetime, timedelta
from app.models.device import DeviceMaster, DeviceHealth
from app.models.alert import Alert
from app.models.sensor_data import SensorData
from app.config import settings
import pandas as pd
import io
import logging
import snowflake.connector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnalyticsService")

def get_snowflake_connection():
    return snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        account=settings.SNOWFLAKE_ACCOUNT,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_SCHEMA,
        role=settings.SNOWFLAKE_ROLE
    )

def map_metric_to_snowflake(metric_col: str) -> str:
    mapping = {
        "temperature": "TEMPERATURE",
        "humidity": "HUMIDITY",
        "pressure": "PRESSURE",
        "vibration": "VIBRATION",
        "voltage": "VOLTAGE",
        "current": "CURRENT_AMPS"
    }
    return mapping.get(metric_col.lower(), metric_col.upper())

def get_trend_data_from_snowflake(metric_col: str, time_range: str, device_id: str = None):
    now = datetime.utcnow()
    if time_range == "1h":
        start_time = now - timedelta(hours=1)
        trunc = "minute"
    elif time_range == "6h":
        start_time = now - timedelta(hours=6)
        trunc = "minute"
    elif time_range == "24h":
        start_time = now - timedelta(hours=24)
        trunc = "hour"
    else: # 7d
        start_time = now - timedelta(days=7)
        trunc = "hour"

    snowflake_metric = map_metric_to_snowflake(metric_col)
    
    query = f"""
        SELECT 
            DATE_TRUNC('{trunc}', F.READING_TIMESTAMP) AS bucket,
            D.DEVICE_ID,
            AVG(F.{snowflake_metric}) AS avg_val
        FROM ANALYTICS.FACT_SENSOR_DATA F
        JOIN ANALYTICS.DIM_DEVICE D ON F.DEVICE_KEY = D.DEVICE_KEY
        WHERE F.READING_TIMESTAMP >= %s
    """
    params = [start_time]
    
    if device_id:
        query += " AND D.DEVICE_ID = %s"
        params.append(device_id)
        
    query += " GROUP BY bucket, D.DEVICE_ID ORDER BY bucket"
    
    conn = get_snowflake_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        data = []
        for row in rows:
            data.append({
                "timestamp": row[0],
                "device_id": row[1],
                "value": float(row[2]) if row[2] is not None else 0.0
            })
        return {"data": data, "metric": metric_col}
    finally:
        conn.close()

def export_data_from_snowflake(format: str, metric: str = None, start_date=None, end_date=None):
    query = """
        SELECT 
            F.READING_TIMESTAMP as timestamp,
            D.DEVICE_ID as device_id,
            F.TEMPERATURE as temperature,
            F.VIBRATION as vibration,
            F.PRESSURE as pressure,
            F.HUMIDITY as humidity,
            F.VOLTAGE as voltage,
            F.CURRENT_AMPS as current
        FROM ANALYTICS.FACT_SENSOR_DATA F
        JOIN ANALYTICS.DIM_DEVICE D ON F.DEVICE_KEY = D.DEVICE_KEY
        WHERE 1=1
    """
    params = []
    if start_date:
        query += " AND F.READING_TIMESTAMP >= %s"
        params.append(start_date)
    if end_date:
        query += " AND F.READING_TIMESTAMP <= %s"
        params.append(end_date)
        
    query += " LIMIT 10000"
    
    conn = get_snowflake_connection()
    try:
        # Load directly using pandas read_sql
        df = pd.read_sql(query, conn, params=params)
        df.columns = [col.lower() for col in df.columns]
        if 'current_amps' in df.columns:
            df.rename(columns={'current_amps': 'current'}, inplace=True)
            
        if metric:
            cols_to_keep = ['timestamp', 'device_id', metric]
            df = df[cols_to_keep]
            
        if format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            return output.getvalue(), "text/csv"
        elif format == 'xlsx':
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            return output.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    finally:
        conn.close()

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
    if settings.SNOWFLAKE_ENABLED:
        try:
            logger.info(f"Querying analytics trend data from Snowflake for metric: {metric_col}")
            return get_trend_data_from_snowflake(metric_col, time_range, device_id)
        except Exception as e:
            logger.error(f"Snowflake query failed: {e}. Falling back to PostgreSQL database.")

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

    if interval.endswith("minute") or interval.endswith("minutes"):
        trunc = "minute"
    else:
        trunc = "hour"

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
    return [{"device_id": h.device_id, "score": float(h.health_score)} for h in health_records]

def export_data(db: Session, format: str, metric: str = None, start_date=None, end_date=None):
    if settings.SNOWFLAKE_ENABLED:
        try:
            logger.info("Exporting historical sensor data from Snowflake...")
            return export_data_from_snowflake(format, metric, start_date, end_date)
        except Exception as e:
            logger.error(f"Snowflake export failed: {e}. Falling back to PostgreSQL database.")

    query = db.query(SensorData)
    if start_date: query = query.filter(SensorData.timestamp >= start_date)
    if end_date: query = query.filter(SensorData.timestamp <= end_date)
    
    data = query.limit(10000).all()
    
    dict_data = []
    for d in data:
        row = {"timestamp": d.timestamp, "device_id": d.device_id}
        if metric == "temperature" or not metric: row["temperature"] = d.temperature
        if metric == "vibration" or not metric: row["vibration"] = d.vibration
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
