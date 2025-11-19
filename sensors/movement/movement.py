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

def read_movement():
    return random.choice([0, 1])

while True:
    time.sleep(60)
    message = {
        "uuid": uuid_str,
        "room_id": room_id,
        "value": read_movement()
    }
    if message.get('value') == 0:
        continue
    message = json.dumps(message)
    print(f"Publishing message: {message}")
    client.publish("sensors/movement", payload=message, qos=1)