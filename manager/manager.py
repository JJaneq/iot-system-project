import paho.mqtt.client as mqtt
import db_manager
import random
import time
import json
from dotenv import load_dotenv
import os
load_dotenv()
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
print(f"Connecting to database {db_name} with user {db_user}")
db = db_manager.DBManager(db_name, db_user, db_password)

def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    client.subscribe("sensors/light_level", qos=1)
    client.subscribe("sensors/temperature", qos=1)
    client.subscribe("sensors/humidity", qos=1)
    client.subscribe("sensors/movement", qos=1)

def on_message(client, userdata, msg):
    print(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
    if msg.topic == "sensors/light_level":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        value = data.get("value")
        db.insert_sensor_data(sensor_id, value)
    elif msg.topic == "sensors/temperature":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        value = data.get("value")
        db.insert_sensor_data(sensor_id, value)
    elif msg.topic == "sensors/humidity":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        value = data.get("value")
        db.insert_sensor_data(sensor_id, value)
    elif msg.topic == "sensors/movement":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        db.insert_sensor_data(sensor_id)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect("mqtt_broker", 1883, 60)
client.loop_forever()

