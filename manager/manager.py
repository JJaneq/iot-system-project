import paho.mqtt.client as mqtt
import random
import time
import json

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe("sensors/light_level", qos=1)
    client.subscribe("sensors/temperature", qos=1)
    client.subscribe("sensors/humidity", qos=1)
    client.subscribe("sensors/movement", qos=1)

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == "sensors/light_level":
        print("Processing light level data")
    elif msg.topic == "sensors/temperature":
        print("Processing temperature data")
    elif msg.topic == "sensors/humidity":
        print("Processing humidity data")
    elif msg.topic == "sensors/movement":
        print("Processing movement data")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt_broker", 1883, 60)
client.loop_forever()

