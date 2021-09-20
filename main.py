import asyncio
import websockets
import json
import sys
from config import BOT_TOKEN


token = BOT_TOKEN


class Connect:
    def __init__(self, token):
        self.session = "null"
        self.token = token
        asyncio.run(self.main())

    async def send_json(self, ws, message):
        await ws.send(json.dumps(message))

    async def rec_json(self, ws):
        response = await ws.recv()
        return json.loads(response)

    async def send_heartbeats(self, ws, interval):
        while True:
            jsonPayload = {
                "op": 1,
                "d": self.session
            }
            await self.send_json(ws, jsonPayload)
            print('HEARTBEAT SENT')
            await asyncio.sleep(interval)

    async def identify(self, ws):
        identify_payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": 513,
                "properties": {
                    "$os": "linux",
                    "$browser": "my_library",
                    "$device": "my_library"
                }
            }
        }
        await self.send_json(ws, identify_payload)

    async def main(self):
        async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
            event = await self.rec_json(ws)
            try:
                heartbeat_interval = event["d"]["heartbeat_interval"] / 1000
                self.session = event['s']
                print("successfully connected to gateway")
            except Exception as e:
                sys.exit(e)
            task1 = asyncio.create_task(
                self.send_heartbeats(ws, heartbeat_interval))
            await self.identify(ws)
            while True:
                event = await self.rec_json(ws)
                if event["t"] == 'READY':
                    print("bot is now ready")
                elif event["op"] == 11:
                    print('HEARTBEAT RECEIVED')
                elif event["op"] == 1:
                    jsonPayload = {
                        "op": 1,
                        "d": "null"
                    }
                    await self.send_json(ws, jsonPayload)
                else:
                    print(event)
                self.session = event['s']


if __name__ == "__main__":
    Connect(BOT_TOKEN)
