from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class SensorData(Base):
    __tablename__ = "sensor_data"
    
    # Note: In postgres this table is partitioned, but SQLAlchemy can still map to it
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("device_master.device_id"), primary_key=True)
    timestamp = Column(DateTime(timezone=False), primary_key=True)
    temperature = Column(Numeric(8, 3))
    humidity = Column(Numeric(8, 3))
    pressure = Column(Numeric(8, 3))
    vibration = Column(Numeric(8, 4))
    voltage = Column(Numeric(8, 3))
    current = Column(Numeric(8, 3))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("DeviceMaster", back_populates="sensor_data")
