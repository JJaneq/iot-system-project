import os
import paho.mqtt.client as mqtt
import random
import time
import json
import uuid
from dotenv import load_dotenv
load_dotenv()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("mqtt_broker", 1883, 60)
client.loop_start()
uuid_str = str(os.getenv("UUID"))

def read_light_level():
    return round(random.uniform(0.0, 100.0), 2)

while True:
    message = {
        "uuid": uuid_str,
        "value": read_light_level()
    }
    message = json.dumps(message)
    print(f"Publishing message: {message}")
    client.publish("sensors/light_level", payload=message, qos=1)
    time.sleep(60)