import paho.mqtt.client as mqtt
import random
import time
import json
import uuid

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("mqtt_broker", 1883, 60)
client.loop_start()
uuid_str = str(uuid.uuid4())

def read_temperature():
    return round(random.uniform(20.0, 30.0), 2)

while True:
    message = {
        "uuid": uuid_str,
        "value": read_temperature()
    }
    message = json.dumps(message)
    print(f"Publishing message: {message}")
    client.publish("sensors/temperature", payload=message, qos=1)
    time.sleep(60)