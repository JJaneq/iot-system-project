from time import sleep
import paho.mqtt.client as mqtt
import db_manager
import os
import json
from ws_server import connections
import asyncio
from ws_server import queue
from dotenv import load_dotenv
import logging
import sys
load_dotenv()

db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db = db_manager.DBManager(db_name, db_user, db_password)

sensors = db.get_all_sensors()
activators = db.get_all_activators()
for activator in activators:
    activator['status'] = "OFF"
    activator['auto'] = True
# i tak tego nie rozszerzamy
room_lights = {
    '1': 'HIGH',
    '2': 'HIGH'
}

alarm_status = {
    '1': 'OFF',
    '2': 'ON'   #na testy
}

logger = logging.getLogger("MQTT_Manager")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

def on_connect(client, userdata, flags, rc, properties):
    logger.info("Connected with result code " + str(rc))
    client.subscribe("sensors/light_level", qos=1)
    client.subscribe("sensors/temperature", qos=1)
    client.subscribe("sensors/humidity", qos=1)
    client.subscribe("sensors/movement", qos=1)
    client.subscribe("activators/update", qos=1)

def on_message(client, userdata, msg):
    logger.info(f"Message received on topic {msg.topic}: {msg.payload.decode()}")
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
            if str(act['room_number']) == str(data.get("room_id")) and act['type'] in ['heater'] and act['auto']:
                activator = act
                break
        if activator is None:
            logger.info("No activator found for temperature analysis")
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
            if str(act['room_number']) == str(data.get("room_id")) and act['type'] in ['vent'] and act['auto']:
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
    elif msg.topic == "activators/update":
        activator_update = json.loads(msg.payload.decode())
        logger.info(f"Activator update received: {activator_update}")
        for act in activators:
            if str(act['id']) == str(activator_update.get("id")):
                # if activator_update.get("auto") == True:
                #     break
                act['status'] = activator_update.get("status").upper()
                act['auto'] = activator_update.get("auto")
                
                logger.info(f"Manual mode activator control. Sending command to activator {act['id']}")
                if act['type'] == 'heater':
                    if act['status'] == 'ON':
                        client.publish(f'hac/control-{act["room_number"]}', 'HEATER/ON')
                    else:
                        client.publish(f'hac/control-{act["room_number"]}', 'HEATER/OFF')
                elif act['type'] == 'vent':
                    if act['status'] == 'ON':
                        client.publish(f'vent/control-{act["room_number"]}', 'OPEN')
                    else:
                        client.publish(f'vent/control-{act["room_number"]}', 'CLOSE')
                elif act['type'] == 'light':
                    if act['status'] == 'ON':
                        client.publish(f'light/control-{act["room_number"]}', 'ON')
                    else:
                        client.publish(f'light/control-{act["room_number"]}', 'OFF')
                elif act['type'] == 'alarm':
                    if act['status'] == 'ON':
                        alarm_status[act['room_number']] = 'ON'
                        client.publish(f'alarm/control-{act["room_number"]}', 'ON')
                    else:
                        alarm_status[act['room_number']] = 'OFF'
                        client.publish(f'alarm/control-{act["room_number"]}', 'OFF')
                break

    # logger.info("Putting message to WebSocket queue")
    
    # push do WebSocket
    payload = json.loads(msg.payload.decode())
    payload["device_type"] = "activator" if msg.topic == "activators/update" else "sensor"
    send_data = {
        "sensor": payload,
        "activators": activators
    }
    json_data = json.dumps(send_data)
    
    # json_activators = json.dumps(activators)
    # payload = json.dumps(payload)
    logger.info(f"Activators: {json_data}")
    queue.put_nowait(json_data)

def temperature_analysis(client, value: float, room_id: int, activator):
    room_thresholds = read_room_thresholds(room_id)
    #Heater control logic
    logger.info(f"Temperature analysis: value={value}, thresholds={room_thresholds}, activator_status={activator['status']}")
    if value < room_thresholds.get("temp_min", 0) and activator['status'] == 'OFF' and activator['type'] == 'heater':
        logger.info("Sending HEATER/ON command")
        activator['status'] = 'ON'
        client.publish(f'hac/control-{room_id}', 'HEATER/ON')
    elif value > room_thresholds.get("temp_max", 100) and activator['status'] == 'ON' and activator['type'] == 'heater':
        logger.info("Sending HEATER/OFF command")
        activator['status'] = 'OFF'
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
        activator['status'] = 'ON'
        logger.info("Sending VENT/OPEN command")
        client.publish(f'vent/control-{room_id}', 'OPEN')
    elif value > room_thresholds.get("humidity_min", 0) and activator['status'] == 'ON':
        activator['status'] = 'OFF'
        logger.info("Sending VENT/CLOSE command")
        client.publish(f'vent/control-{room_id}', 'CLOSE')

def light_level_analysis(client, value: float, room_id: int):
    room_thresholds = read_room_thresholds(room_id)
    if value < room_thresholds.get("light_min", 0):
        logger.info("Setting light level to LOW")
        room_lights[room_id] = 'LOW'
    else:
        logger.info("Setting light level to HIGH")
        room_lights[room_id] = 'HIGH'

def movement_check(client, room_id: int):
    room_light_activator = None
    for act in activators:
        if str(act['room_number']) == str(room_id) and act['type'] in ['light'] and act['auto']:
            room_light_activator = act
            break
    if room_light_activator is None:
        logger.info("No active activator found for movement check")
        return
    if alarm_status[room_id] == 'ON':
        logger.info("Sending ALARM/ON command")
        client.publish(f'alarm/control-{room_id}', 'ON')
    else:
        logger.info("Sending ALARM/OFF command")
        client.publish(f'alarm/control-{room_id}', 'OFF')

    if room_lights[room_id] == 'LOW':
        logger.info("Turning ON the light due to movement")
        client.publish(f'light/control-{room_id}', 'ON')
    else:
        # czyli jak ktoś chce poczytać książkę przy świetle to niech lepiej robi przysiady
        logger.info("Turning OFF the light due to movement")
        client.publish(f'light/control-{room_id}', 'OFF')
    
def read_room_thresholds(room_id: int) -> dict:
    return db.get_room_thresholds(room_id)

def run_mqtt():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("mqtt_broker", 1883, 60)
    client.loop_forever()