import asyncio
import websockets

connections = set()
queue = asyncio.Queue()

async def ws_handler(ws):
    connections.add(ws)
    try:
        async for _ in ws:
            pass
    finally:
        connections.remove(ws)

async def broadcaster():
    while True:
        message = await queue.get()
        for ws in connections:
            await ws.send(message)

async def ws_main():
    async with websockets.serve(ws_handler, "0.0.0.0", 8765):
        await broadcaster()

def run_ws():
    asyncio.run(ws_main())