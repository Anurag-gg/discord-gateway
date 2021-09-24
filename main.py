import asyncio
import websockets
import json
from config import BOT_TOKEN


class Connect:
    def __init__(self, token):
        self.sequence = "null"
        self.token = token
        self.heartbeat_received = True
        self.status = 'identity'
        asyncio.run(self.main())

    async def send_json(self, ws, message):
        await ws.send(json.dumps(message))

    async def rec_json(self, ws):
        response = await ws.recv()
        return json.loads(response)

    async def send_heartbeats(self, ws, interval):
        while True:
            if self.heartbeat_received:
                jsonPayload = {
                    "op": 1,
                    "d": self.sequence
                }
                await self.send_json(ws, jsonPayload)
                print('HEARTBEAT SENT')
                self.heartbeat_received = False
                await asyncio.sleep(interval)
            else:
                print("no heartbeat_ack received")
                ws.frames.Close(1011, reason=None)
                self.status = "resume"
                await self.main()
                break

    async def identify(self, ws):
        identify_payload = {
            "op": 2,
            "d": {
                "token": self.token,
                "intents": 16383,
                "properties": {
                    "$os": "linux",
                    "$browser": "my_library",
                    "$device": "my_library"
                }
            }
        }
        await self.send_json(ws, identify_payload)

    async def resume(self, ws):
        resume_payload = {
            {
                "op": 6,
                "d": {
                    "token": self.token,
                    "session_id": self.session_id,
                    "seq": self.sequence
                }
            }
        }
        await self.send_json(ws, resume_payload)

    async def main(self):
        async with websockets.connect("wss://gateway.discord.gg/?v=9&encoding=json") as ws:
            while True:
                event = await self.rec_json(ws)
                if event["op"] == 10:
                    heartbeat_interval = event["d"]["heartbeat_interval"] / 1000
                    print("successfully connected to gateway")
                    asyncio.create_task(
                        self.send_heartbeats(ws, heartbeat_interval))
                    if self.status == "identity":
                        await self.identify(ws)
                    else:
                        await self.resume(ws)

                elif event["t"] == 'READY':
                    self.session_id = event['d']['session_id']
                    print("bot is now ready")

                elif event["op"] == 11:
                    print('HEARTBEAT RECEIVED')
                    self.heartbeat_received = True

                elif event["op"] == 1:
                    print("op code 1 received")
                    jsonPayload = {
                        "op": 1,
                        "d": self.sequence
                    }
                    await self.send_json(ws, jsonPayload)

                elif event["op"] == 7:
                    print("reconnecting")
                    await self.resume(ws)

                else:
                    print(event)

                self.sequence = event['s']


if __name__ == "__main__":
    Connect(BOT_TOKEN)
