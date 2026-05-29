from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class DeviceMaster(Base):
    __tablename__ = "device_master"

    device_id = Column(String(50), primary_key=True, index=True)
    device_name = Column(String(100), nullable=False)
    device_type = Column(String(50), nullable=False)
    location = Column(String(100))
    install_date = Column(Date)
    status = Column(String(20), default="offline")
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    sensor_data = relationship("SensorData", back_populates="device", lazy="dynamic")
    alerts = relationship("Alert", back_populates="device", lazy="dynamic")
    health = relationship("DeviceHealth", back_populates="device", uselist=False)

class DeviceHealth(Base):
    __tablename__ = "device_health"

    id = Column(Integer, primary_key=True, index=True) # Assuming BIGSERIAL acts like Integer for ORM mapping if we don't need BigInt specifically here or use BigInteger
    device_id = Column(String(50), ForeignKey("device_master.device_id"))
    uptime_percentage = Column(Numeric(5, 2))
    anomaly_count = Column(Integer, default=0)
    health_score = Column(Numeric(5, 2))
    last_seen = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    device = relationship("DeviceMaster", back_populates="health")
