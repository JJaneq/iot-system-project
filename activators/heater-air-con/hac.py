import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
load_dotenv()

uuid = os.getenv("UUID")
room_id = os.getenv("ROOM_ID")

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe(f"hac/control-{room_id}", qos=1)

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == f"hac/control-{room_id}":
        command = msg.payload.decode().lower()
        if command == "AC/OFF":
            print("Turning off Air Conditioner")
        elif command == "AC/COOL":
            print("Setting Air Conditioner to COOL mode")
        elif command == "AC/HEAT":
            print("Setting Air Conditioner to HEAT mode")
        elif command == "HEATER/ON":
            print("Turning on Heater")
        elif command == "HEATER/OFF":
            print("Turning off Heater")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt_broker", 1883, 60)
client.loop_forever()