import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
import logging
import sys
load_dotenv()

uuid = os.getenv("UUID")
room_id = os.getenv("ROOM_ID")

logger = logging.getLogger("HAC_Activator")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def on_connect(client, userdata, flags, rc, properties):
    logger.info("Connected with result code " + str(rc))
    client.subscribe(f"hac/control-{room_id}", qos=1)

def on_message(client, userdata, msg):
    logger.info(f"HAC: Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == f"hac/control-{room_id}":
        command = msg.payload.decode()
        if command == "AC/OFF":
            logger.info("Turning off Air Conditioner")
        elif command == "AC/COOL":
            logger.info("Setting Air Conditioner to COOL mode")
        elif command == "AC/HEAT":
            logger.info("Setting Air Conditioner to HEAT mode")
        elif command == "HEATER/ON":
            logger.info("Turning on Heater")
        elif command == "HEATER/OFF":
            logger.info("Turning off Heater")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt_broker", 1883, 60)
client.loop_forever()