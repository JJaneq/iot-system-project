import paho.mqtt.client as mqtt
from mqtt_manager import run_mqtt
from flask_manager import run_api
import threading


if __name__ == "__main__":
    t1 = threading.Thread(target=run_mqtt)
    t2 = threading.Thread(target=run_api)

    t1.start()
    t2.start()

    t1.join()
    t2.join()