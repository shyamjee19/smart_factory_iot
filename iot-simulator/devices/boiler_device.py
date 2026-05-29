import random
from .base_device import BaseDevice

class BoilerDevice(BaseDevice):
    def __init__(self, device_id: str, location: str):
        super().__init__(device_id, "Boiler", location)
        
    def generate_reading(self) -> dict:
        reading = self.get_base_reading()
        is_anomaly = self._maybe_trigger_anomaly()
        
        if is_anomaly:
            reading["temperature"] = round(random.uniform(210.0, 250.0), 3) # Temp critical anomaly
            reading["vibration"] = round(random.uniform(1.0, 3.0), 4)
            reading["pressure"] = round(random.uniform(11.0, 15.0), 3) # Pressure critical anomaly
            reading["voltage"] = round(random.uniform(200.0, 250.0), 3)
            reading["current"] = round(random.uniform(10.0, 20.0), 3)
            reading["humidity"] = round(random.uniform(80.0, 100.0), 3) # High humidity
        else:
            reading["temperature"] = round(random.uniform(150.0, 200.0), 3) # Normal high temp
            reading["vibration"] = round(random.uniform(0.1, 1.0), 4)
            reading["pressure"] = round(random.uniform(5.0, 10.0), 3) # Normal high pressure
            reading["voltage"] = round(random.uniform(220.0, 240.0), 3)
            reading["current"] = round(random.uniform(5.0, 15.0), 3)
            reading["humidity"] = round(random.uniform(40.0, 70.0), 3)
            
        return reading
