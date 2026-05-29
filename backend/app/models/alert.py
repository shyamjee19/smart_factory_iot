from sqlalchemy import Column, String, Boolean, DateTime, Numeric, ForeignKey, BigInteger, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    device_id = Column(String(50), ForeignKey("device_master.device_id"))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    metric = Column(String(50))
    threshold_value = Column(Numeric(10, 3))
    actual_value = Column(Numeric(10, 3))
    message = Column(Text)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(100))
    acknowledged_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("DeviceMaster", back_populates="alerts")
