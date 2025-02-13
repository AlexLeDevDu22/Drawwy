import asyncio
import json
import websockets

connected_players = {}

async def handler(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "join":
                if len(connected_players) < 8:  # Max 8 joueurs
                    player_id = f"player_{len(connected_players) + 1}"
                    connected_players[player_id] = websocket
                    await websocket.send(json.dumps({"type": "welcome", "player_id": player_id}))
                    print(f"{player_id} a rejoint la partie.")

                    # Envoyer la liste des joueurs actuels à tous
                    await broadcast({"type": "update_players", "players": list(connected_players.keys())})
                else:
                    await websocket.send(json.dumps({"type": "full", "message": "Partie pleine !"}))

            elif data["type"] == "sdp":  # Transfert SDP entre joueurs
                target = connected_players.get(data["target"])
                if target:
                    await target.send(json.dumps(data))

    except websockets.exceptions.ConnectionClosed:
        disconnected = [pid for pid, ws in connected_players.items() if ws == websocket]
        if disconnected:
            del connected_players[disconnected[0]]
            print(f"{disconnected[0]} s'est déconnecté.")
            await broadcast({"type": "update_players", "players": list(connected_players.keys())})

async def broadcast(message):
    """Envoie un message à tous les joueurs connectés."""
    for ws in connected_players.values():
        await ws.send(json.dumps(message))

async def main():
    server = await websockets.serve(handler, "localhost", 8765)
    await server.wait_closed()

asyncio.run(main())