import time
import logging
import signal
import sys
from devices.opc_device import OPCDevice
from devices.conveyor_device import ConveyorDevice
from devices.pump_device import PumpDevice
from devices.motor_device import MotorDevice
from devices.boiler_device import BoilerDevice
from utils.mqtt_publisher import MQTTPublisher
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FactorySimulator:
    def __init__(self):
        self.publisher = MQTTPublisher(config.MQTT_BROKER, config.MQTT_PORT)
        self.devices = []
        self.running = False
        self.messages_published = 0
        self.start_time = None
        self._initialize_devices()

    def _initialize_devices(self):
        device_classes = {
            "OPC": OPCDevice,
            "Conveyor": ConveyorDevice,
            "Pump": PumpDevice,
            "Motor": MotorDevice,
            "Boiler": BoilerDevice
        }
        
        for dev_config in config.DEFAULT_DEVICES:
            device_class = device_classes.get(dev_config["device_type"])
            if device_class:
                device = device_class(dev_config["device_id"], dev_config["location"])
                self.devices.append(device)
                logging.info(f"Initialized device: {device.device_id} ({device.device_type})")
            else:
                logging.warning(f"Unknown device type: {dev_config['device_type']}")

    def _signal_handler(self, sig, frame):
        logging.info("Shutting down simulator gracefully...")
        self.running = False

    def run(self):
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.publisher.connect()
        except Exception as e:
            logging.error(f"Failed to start simulator: {e}")
            sys.exit(1)

        self.running = True
        self.start_time = time.time()
        last_stats_time = self.start_time
        
        logging.info("--- Smart Factory Simulator Started ---")

        while self.running:
            cycle_start = time.time()
            
            for device in self.devices:
                reading = device.generate_reading()
                topic = f"{config.MQTT_TOPIC_PREFIX}{device.location.replace(' ', '_')}/{device.device_type}/{device.device_id}"
                
                if self.publisher.publish(topic, reading):
                    self.messages_published += 1
            
            # Print stats every 30 seconds
            if cycle_start - last_stats_time >= 30:
                elapsed = cycle_start - self.start_time
                rate = self.messages_published / elapsed if elapsed > 0 else 0
                logging.info(f"Stats: Published {self.messages_published} messages. Rate: {rate:.2f} msg/sec.")
                last_stats_time = cycle_start
            
            # Sleep to maintain interval
            elapsed_cycle = time.time() - cycle_start
            sleep_time = max(0, config.PUBLISH_INTERVAL - elapsed_cycle)
            time.sleep(sleep_time)
            
        self.publisher.disconnect()
        logging.info("Simulator stopped.")

if __name__ == "__main__":
    simulator = FactorySimulator()
    simulator.run()
