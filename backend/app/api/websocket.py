import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from jose import JWTError, jwt

from app.database import get_db, SessionLocal
from app.config import settings
from app.models.sensor_data import SensorData
from app.utils.metrics import active_connections, messages_sent

router = APIRouter()
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        active_connections.inc()
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            active_connections.dec()
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_live_data(self):
        if not self.active_connections:
            return
            
        # Get DB session just for this broadcast tick
        db = SessionLocal()
        try:
            # In a real heavy-load scenario, we might want to subscribe to Redis/Kafka 
            # instead of querying Postgres repeatedly.
            # For this demo, we query the latest row for each device.
            
            # Simple approach: get the latest 5 rows (assuming 5 devices)
            latest_readings = db.query(SensorData).order_by(desc(SensorData.timestamp)).limit(5).all()
            
            data = []
            for r in latest_readings:
                data.append({
                    "device_id": r.device_id,
                    "timestamp": r.timestamp.isoformat(),
                    "temperature": float(r.temperature) if r.temperature else None,
                    "vibration": float(r.vibration) if r.vibration else None,
                    "pressure": float(r.pressure) if r.pressure else None
                })
            
            message = json.dumps({"type": "live_sensor_data", "data": data})
            
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                    messages_sent.inc()
                except Exception as e:
                    logger.error(f"Error sending to WS client: {e}")
                    # The disconnect will be handled in the main endpoint
                    
        except Exception as e:
            logger.error(f"Error in broadcast loop: {e}")
        finally:
            db.close()

manager = ConnectionManager()

# Background task to broadcast data every 2 seconds
async def broadcast_task():
    while True:
        await manager.broadcast_live_data()
        await asyncio.sleep(2.0)

# We start the background task when the module is loaded
# A better place in a real app would be in main.py startup event
asyncio.create_task(broadcast_task())

async def verify_ws_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return False
        return True
    except JWTError:
        return False

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
    if not token or not await verify_ws_token(token):
        logger.warning("WebSocket connection attempt with invalid token.")
        await websocket.close(code=1008)
        return
        
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open, wait for client messages (if any)
            # Mostly we just broadcast to them from the background task
            data = await websocket.receive_text()
            # We don't really expect messages from the dashboard, but handle ping/pong if needed
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
