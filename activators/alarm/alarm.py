import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
load_dotenv()

uuid = os.getenv("UUID")
room_id = os.getenv("ROOM_ID")

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(f"alarm/control-{room_id}", qos=1)

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == f"alarm/control-{room_id}":
        command = msg.payload.decode()
        if command == "ON":
            print("Alarm ON...")
        elif command == "OFF":
            print("Alarm OFF...")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt_broker", 1883, 60)
client.loop_forever()