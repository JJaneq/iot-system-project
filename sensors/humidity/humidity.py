import paho.mqtt.client as mqtt
import random
import time
import json
import os

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("mqtt_broker", 1883, 60)
client.loop_start()
uuid_str = os.getenv("UUID")

if not uuid_str:
    print("UUID environment variable not set. Exiting.")
    exit(1)

def read_humidity():
    return round(random.uniform(30.0, 90.0), 2)

while True:
    message = {
        "uuid": uuid_str,
        "value": read_humidity()
    }
    message = json.dumps(message)
    print(f"Publishing message: {message}")
    client.publish("sensors/humidity", payload=message, qos=1)
    time.sleep(60)