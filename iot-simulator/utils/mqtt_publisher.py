import json
import logging
import time
import paho.mqtt.client as mqtt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MQTTPublisher:
    def __init__(self, broker: str, port: int):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id=f"iot-simulator-{int(time.time())}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info(f"Connected to MQTT broker at {self.broker}:{self.port}")
        else:
            logging.error(f"Failed to connect to MQTT broker. Return code: {rc}")
            
    def _on_disconnect(self, client, userdata, rc):
        logging.warning("Disconnected from MQTT broker. Attempting to reconnect...")
        if rc != 0:
            try:
                self.client.reconnect()
            except Exception as e:
                logging.error(f"Reconnection failed: {e}")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Connection failed: {e}")
            raise
            
    def publish(self, topic: str, payload: dict):
        try:
            json_payload = json.dumps(payload)
            result = self.client.publish(topic, json_payload, qos=1)
            # result.wait_for_publish() # Uncomment for synchronous publishing (slower)
            logging.debug(f"Published to {topic}: {json_payload}")
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logging.error(f"Failed to publish to {topic}: {e}")
            return False

    def disconnect(self):
        logging.info("Disconnecting from MQTT broker...")
        self.client.loop_stop()
        self.client.disconnect()
