import random
from .base_device import BaseDevice

class PumpDevice(BaseDevice):
    def __init__(self, device_id: str, location: str):
        super().__init__(device_id, "Pump", location)
        
    def generate_reading(self) -> dict:
        reading = self.get_base_reading()
        is_anomaly = self._maybe_trigger_anomaly()
        
        if is_anomaly:
            reading["temperature"] = round(random.uniform(65.0, 85.0), 3)
            reading["vibration"] = round(random.uniform(4.0, 9.0), 4)
            reading["pressure"] = round(random.uniform(7.0, 10.0), 3) # Pressure critical anomaly
            reading["voltage"] = round(random.uniform(200.0, 250.0), 3)
            reading["current"] = round(random.uniform(15.0, 25.0), 3)
            reading["humidity"] = round(random.uniform(70.0, 90.0), 3)
        else:
            reading["temperature"] = round(random.uniform(40.0, 60.0), 3)
            reading["vibration"] = round(random.uniform(0.5, 2.5), 4)
            reading["pressure"] = round(random.uniform(2.0, 6.0), 3) # Normal pressure
            reading["voltage"] = round(random.uniform(220.0, 240.0), 3)
            reading["current"] = round(random.uniform(8.0, 12.0), 3)
            reading["humidity"] = round(random.uniform(50.0, 70.0), 3)
            
        return reading
