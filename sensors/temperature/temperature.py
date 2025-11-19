import paho.mqtt.client as mqtt
import random
import time
import json
import os
from dotenv import load_dotenv
load_dotenv()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("mqtt_broker", 1883, 60)
client.loop_start()
uuid_str = str(os.getenv("UUID"))
room_id = os.getenv("ROOM_ID")

def read_temperature():
    # return round(random.uniform(20.0, 30.0), 2)
    return random.choice([-100, 100])

while True:
    message = {
        "uuid": uuid_str,
        "room_id": room_id,
        "value": read_temperature()
    }
    message = json.dumps(message)
    print(f"Publishing message: {message}")
    client.publish("sensors/temperature", payload=message, qos=1)
    time.sleep(60)