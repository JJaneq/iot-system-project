import asyncio
import websockets
import json
import paho.mqtt.client as mqtt

connections = set()
queue = asyncio.Queue()

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqtt_client.connect("mqtt_broker", 1883, 60)
mqtt_client.loop_start() 

async def ws_handler(ws):
    connections.add(ws)
    try:
        async for msg in ws:
            try:
                mqtt_client.publish("activators/update", msg, qos=1)
                print("WebSocket → MQTT:", msg)
            except Exception as e:
                print("Błąd MQTT:", e)
    finally:
        connections.remove(ws)

async def broadcaster():
    while True:
        message, activators = await queue.get()
        for ws in connections:
            await ws.send(message)
            await ws.send(activators)

async def ws_main():
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        asyncio.create_task(broadcaster())
        await asyncio.Future()

def run_ws():
    asyncio.run(ws_main())