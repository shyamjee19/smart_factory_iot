import random
import datetime
from abc import ABC, abstractmethod

class BaseDevice(ABC):
    def __init__(self, device_id: str, device_type: str, location: str):
        self.device_id = device_id
        self.device_type = device_type
        self.location = location
        self.status = "online"
        self._anomaly_counter = 0

    def _maybe_trigger_anomaly(self) -> bool:
        """5% chance to trigger an anomaly state for a short duration."""
        if self._anomaly_counter > 0:
            self._anomaly_counter -= 1
            if self._anomaly_counter == 0:
                 self.status = "online" # Recover
            return True
        
        if random.random() < 0.05:
            self._anomaly_counter = random.randint(3, 10) # Stay anomalous for a few cycles
            self.status = random.choice(["warning", "critical"])
            return True
        
        return False

    def get_base_reading(self) -> dict:
        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "location": self.location,
            "status": self.status
        }

    @abstractmethod
    def generate_reading(self) -> dict:
        """Returns a dict with all sensor values."""
        pass
