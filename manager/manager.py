import paho.mqtt.client as mqtt
from mqtt_manager import run_mqtt
from flask_manager import run_api
import threading
from ws_server import run_ws, connections

if __name__ == "__main__":
    t1 = threading.Thread(target=run_mqtt)
    t2 = threading.Thread(target=run_api)
    t3 = threading.Thread(target=run_ws)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()