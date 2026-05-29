import os
import json
import time
import logging
import signal
import sys
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
from kafka import KafkaProducer
from kafka.errors import KafkaError

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("MQTT-Kafka-Bridge")

# Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC_PREFIX", "factory/") + "#"

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_SENSOR", "factory.sensor.raw")

class Bridge:
    def __init__(self):
        self.running = False
        self.messages_processed = 0
        self.start_time = time.time()
        
        # Initialize Kafka Producer
        self._init_kafka()
        
        # Initialize MQTT Client
        self.mqtt_client = mqtt.Client(client_id=f"bridge-{int(time.time())}")
        self.mqtt_client.on_connect = self.on_mqtt_connect
        self.mqtt_client.on_message = self.on_mqtt_message
        self.mqtt_client.on_disconnect = self.on_mqtt_disconnect

    def _init_kafka(self):
        retries = 5
        while retries > 0:
            try:
                logger.info(f"Connecting to Kafka at {KAFKA_BROKER}...")
                self.kafka_producer = KafkaProducer(
                    bootstrap_servers=KAFKA_BROKER,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    key_serializer=lambda k: k.encode('utf-8') if k else None,
                    retries=5
                )
                logger.info("Successfully connected to Kafka.")
                return
            except KafkaError as e:
                logger.error(f"Failed to connect to Kafka: {e}")
                retries -= 1
                if retries == 0:
                    logger.critical("Could not connect to Kafka after multiple attempts. Exiting.")
                    sys.exit(1)
                time.sleep(5)

    def on_mqtt_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
            client.subscribe(MQTT_TOPIC)
            logger.info(f"Subscribed to topic: {MQTT_TOPIC}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def on_mqtt_disconnect(self, client, userdata, rc):
        logger.warning("Disconnected from MQTT broker.")
        if rc != 0:
            logger.info("Attempting to reconnect...")

    def on_mqtt_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            device_id = payload.get("device_id")
            
            # Send to Kafka
            future = self.kafka_producer.send(
                topic=KAFKA_TOPIC,
                key=device_id,
                value=payload
            )
            # future.get(timeout=10) # Block for synchronous send (slower)
            
            self.messages_processed += 1
            if self.messages_processed % 100 == 0:
                logger.info(f"Processed {self.messages_processed} messages so far.")
                
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received on {msg.topic}: {msg.payload}")
        except Exception as e:
            logger.error(f"Error processing message from {msg.topic}: {e}")

    def _signal_handler(self, sig, frame):
        logger.info("Shutting down bridge gracefully...")
        self.running = False
        self.mqtt_client.disconnect()
        self.kafka_producer.flush()
        self.kafka_producer.close()
        
    def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("Starting MQTT to Kafka Bridge...")
        try:
            self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.running = True
            
            # Loop forever
            self.mqtt_client.loop_forever()
            
        except Exception as e:
            logger.error(f"Bridge failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    bridge = Bridge()
    bridge.run()
