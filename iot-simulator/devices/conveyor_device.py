import random
from .base_device import BaseDevice

class ConveyorDevice(BaseDevice):
    def __init__(self, device_id: str, location: str):
        super().__init__(device_id, "Conveyor", location)
        
    def generate_reading(self) -> dict:
        reading = self.get_base_reading()
        is_anomaly = self._maybe_trigger_anomaly()
        
        if is_anomaly:
            reading["temperature"] = round(random.uniform(50.0, 70.0), 3)
            reading["vibration"] = round(random.uniform(6.0, 12.0), 4) # Very high vibration
            reading["pressure"] = round(random.uniform(1.0, 2.0), 3)
            reading["voltage"] = round(random.uniform(180.0, 260.0), 3)
            reading["current"] = round(random.uniform(20.0, 40.0), 3)
            reading["humidity"] = round(random.uniform(50.0, 70.0), 3)
        else:
            reading["temperature"] = round(random.uniform(30.0, 45.0), 3)
            reading["vibration"] = round(random.uniform(1.0, 5.0), 4) # Normally vibrates more than OPC
            reading["pressure"] = round(random.uniform(1.0, 2.0), 3)
            reading["voltage"] = round(random.uniform(220.0, 240.0), 3)
            reading["current"] = round(random.uniform(5.0, 15.0), 3)
            reading["humidity"] = round(random.uniform(40.0, 60.0), 3)
            
        return reading
