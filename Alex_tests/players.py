import asyncio
import json
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription

player_id = None
pc = RTCPeerConnection()

async def receive_messages(websocket):
    global player_id
    async for message in websocket:
        data = json.loads(message)

        if data["type"] == "welcome":
            player_id = data["player_id"]
            print(f"Rejoint en tant que {player_id}")

        elif data["type"] == "update_players":
            print("Joueurs connectés :", data["players"])

        elif data["type"] == "sdp":
            offer = RTCSessionDescription(sdp=data["sdp"], type=data["sdp_type"])
            await pc.setRemoteDescription(offer)
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            await websocket.send(json.dumps({"type": "sdp", "target": data["sender"], "sdp": pc.localDescription.sdp, "sdp_type": pc.localDescription.type}))

async def main():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "join"}))
        asyncio.create_task(receive_messages(websocket))

        # Création du SDP et envoi au serveur
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        await websocket.send(json.dumps({"type": "sdp", "sdp": pc.localDescription.sdp, "sdp_type": "offer"}))

        while True:
            await asyncio.sleep(1)  # Laisse tourner le script

asyncio.run(main())
