import websockets
import asyncio

async def main():
    uri = "wss://vital-mastiff-publicly.ngrok-free.app/socket.io/?transport=websocket"
    async with websockets.connect(uri) as websocket:
        await websocket.send("Hello, WebSocket!")
        response = await websocket.recv()
        print(f"Received: {response}")

asyncio.run(main())
