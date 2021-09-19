import asyncio
import websockets
import json
import sys
from config import BOT_TOKEN


token = BOT_TOKEN


async def send_json(ws, message):
    await ws.send(json.dumps(message))


async def rec_json(ws):
    response = await ws.recv()
    return json.loads(response)


async def send_heartbeats(ws, interval):
    while True:
        jsonPayload = {
            "op": 1,
            "d": "null"
        }
        await send_json(ws, jsonPayload)
        print('HEARTBEAT SENT')
        await asyncio.sleep(interval)


async def identify(ws):
    identify_payload = {
        "op": 2,
        "d": {
            "token": token,
            "intents": 513,
            "properties": {
                "$os": "linux",
                "$browser": "my_library",
                "$device": "my_library"
            }
        }
    }
    await send_json(ws, identify_payload)


async def main():
    async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
        event = await rec_json(ws)
        try:
            heartbeat_interval = event["d"]["heartbeat_interval"] / 1000
            print("successfully connected to gateway")
        except Exception as e:
            sys.exit(e)
        task1 = asyncio.create_task(send_heartbeats(ws, heartbeat_interval))
        await identify(ws)
        while True:
            event = await rec_json(ws)
            if event["t"] == 'READY':
                print("bot is now ready")
            elif event["op"] == 11:
                print('HEARTBEAT RECEIVED')
            elif event["op"] == 1:
                jsonPayload = {
                    "op": 1,
                    "d": "null"
                }
                await send_json(ws, jsonPayload)
            else:
                print(event)


asyncio.run(main())
