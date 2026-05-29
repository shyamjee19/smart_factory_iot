import random
from .base_device import BaseDevice

class MotorDevice(BaseDevice):
    def __init__(self, device_id: str, location: str):
        super().__init__(device_id, "Motor", location)
        
    def generate_reading(self) -> dict:
        reading = self.get_base_reading()
        is_anomaly = self._maybe_trigger_anomaly()
        
        if is_anomaly:
            reading["temperature"] = round(random.uniform(80.0, 100.0), 3)
            reading["vibration"] = round(random.uniform(4.0, 8.0), 4) # High vibration
            reading["pressure"] = round(random.uniform(1.0, 2.0), 3) 
            reading["voltage"] = round(random.uniform(180.0, 260.0), 3)
            reading["current"] = round(random.uniform(35.0, 50.0), 3) # Current critical anomaly
            reading["humidity"] = round(random.uniform(40.0, 60.0), 3)
        else:
            reading["temperature"] = round(random.uniform(50.0, 75.0), 3)
            reading["vibration"] = round(random.uniform(0.5, 3.0), 4)
            reading["pressure"] = round(random.uniform(1.0, 2.0), 3)
            reading["voltage"] = round(random.uniform(220.0, 240.0), 3)
            reading["current"] = round(random.uniform(10.0, 30.0), 3) # Normal current
            reading["humidity"] = round(random.uniform(30.0, 50.0), 3)
            
        return reading
