import os
from dotenv import load_dotenv

load_dotenv()

# MQTT Settings
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC_PREFIX = os.getenv("MQTT_TOPIC_PREFIX", "factory/")

# Simulator Settings
PUBLISH_INTERVAL = 2  # seconds between readings
DEVICE_COUNT = 5 # Number of distinct devices to simulate

# Default Device Metadata (Used if database seeding isn't available)
DEFAULT_DEVICES = [
    {
        "device_id": "DEV-OPC-001",
        "device_type": "OPC",
        "location": "Assembly Line A"
    },
    {
        "device_id": "DEV-CONV-001",
        "device_type": "Conveyor",
        "location": "Packaging Zone B"
    },
    {
        "device_id": "DEV-PUMP-001",
        "device_type": "Pump",
        "location": "Cooling System C"
    },
    {
        "device_id": "DEV-MOTOR-001",
        "device_type": "Motor",
        "location": "Drive Unit D"
    },
    {
        "device_id": "DEV-BOILER-001",
        "device_type": "Boiler",
        "location": "Boiler Room E"
    }
]
