from time import sleep
import paho.mqtt.client as mqtt
import db_manager
import os
import json
from ws_server import connections
import asyncio
from ws_server import queue
from dotenv import load_dotenv
load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db = db_manager.DBManager(db_name, db_user, db_password)

sensors = db.get_all_sensors()
activators = db.get_all_activators()
for activator in activators:
    activator['status'] = "OFF"
# i tak tego nie rozszerzamy
room_lights = {
    '1': 'HIGH',
    '2': 'HIGH'
}

alarm_status = {
    '1': 'OFF',
    '2': 'ON'   #na testy
}

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
        light_level_analysis(client, value, data.get("room_id"))
    elif msg.topic == "sensors/temperature":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        value = data.get("value")
        db.insert_sensor_data(sensor_id, value)
        activator = None
        for act in activators:
            if str(act['room_number']) == str(data.get("room_id")) and act['type'] in ['heater']:
                activator = act
                break
        if activator is None:
            print("No activator found for temperature analysis")
            return
        humidity_analysis(client, value, data.get("room_id"), activator)
        temperature_analysis(client, value, data.get("room_id"), activator)
    elif msg.topic == "sensors/humidity":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        value = data.get("value")
        db.insert_sensor_data(sensor_id, value)
        # mocno nieoptymalne ale chcę od tego odejść zostawiając coś co działa
        activator = None
        for act in activators:
            if str(act['room_number']) == str(data.get("room_id")) and act['type'] in ['vent']:
                activator = act
                break
        if activator is None:
            print("No activator found for humidity analysis")
            return
        humidity_analysis(client, value, data.get("room_id"), activator)
    elif msg.topic == "sensors/movement":
        data = json.loads(msg.payload.decode())
        sensor_id = data.get("uuid")
        db.insert_sensor_data(sensor_id)
        movement_check(client, data.get("room_id"))
    
    # push do WebSocket
    payload = msg.payload.decode()
    queue.put_nowait(payload)

def temperature_analysis(client, value: float, room_id: int, activator):
    room_thresholds = read_room_thresholds(room_id)
    #Heater control logic
    if value < room_thresholds.get("temp_min", 0) and activator['status'] == 'OFF' and activator['type'] == 'heater':
        print("Sending HEATER/ON command")
        client.publish(f'hac/control-{room_id}', 'HEATER/ON')
    elif value > room_thresholds.get("temp_max", 100) and activator['status'] == 'ON' and activator['type'] == 'heater':
        print("Sending HEATER/OFF command")
        client.publish(f'hac/control-{room_id}', 'HEATER/OFF')

    #AC control logic
    # może lepiej ręcznie ustawiać tryby AC zamiast włączać i wyłączać?
    # if value > room_thresholds.get("temp_max", 100) and activator['status'] == 'OFF' and activator['type'] == 'air_conditioner':
    #     mqtt.Client.publish(f'temperature/control-{room_id}', 'AC/COOL')
    # elif value < room_thresholds.get("temp_min", 0) and activator['status'] == 'OFF' and activator['type'] == 'air_conditioner':
    #     mqtt.Client.publish(f'temperature/control-{room_id}', 'AC/HEAT')
    # elif room_thresholds.get("temp_min", 0) <= value <= room_thresholds.get("temp_max", 100) and activator['status'] == 'ON' and activator['type'] == 'air_conditioner':
    #     mqtt.Client.publish(f'temperature/control-{room_id}', 'AC/OFF')

def humidity_analysis(client, value: float, room_id: int, activator):
    room_thresholds = read_room_thresholds(room_id)
    # włączamy jak jest wilgotno, a jak spadnie poniżej min to zamykamy
    if value > room_thresholds.get("humidity_max", 100) and activator['status'] == 'OFF':
        print("Sending VENT/OPEN command")
        client.publish(f'vent/control-{room_id}', 'OPEN')
    elif value > room_thresholds.get("humidity_min", 0) and activator['status'] == 'ON':
        print("Sending VENT/CLOSE command")
        client.publish(f'vent/control-{room_id}', 'CLOSE')

def light_level_analysis(client, value: float, room_id: int):
    room_thresholds = read_room_thresholds(room_id)
    if value < room_thresholds.get("light_min", 0):
        print("Setting light level to LOW")
        room_lights[room_id] = 'LOW'
    else:
        print("Setting light level to HIGH")
        room_lights[room_id] = 'HIGH'

def movement_check(client, room_id: int):
    if alarm_status[room_id] == 'ON':
        print("Sending ALARM/ON command")
        client.publish(f'alarm/control-{room_id}', 'ON')
    else:
        print("Sending ALARM/OFF command")
        client.publish(f'alarm/control-{room_id}', 'OFF')

    if room_lights[room_id] == 'LOW':
        print("Turning ON the light due to movement")
        client.publish(f'light/control-{room_id}', 'ON')
    else:
        # czyli jak ktoś chce poczytać książkę przy świetle to niech lepiej robi przysiady
        print("Turning OFF the light due to movement")
        client.publish(f'light/control-{room_id}', 'OFF')
    
def read_room_thresholds(room_id: int) -> dict:
    return db.get_room_thresholds(room_id)

def run_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("mqtt_broker", 1883, 60)
    client.loop_forever()