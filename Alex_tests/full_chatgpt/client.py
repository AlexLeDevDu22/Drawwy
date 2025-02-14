import asyncio
import websockets
import json

# Met ici l'URL donnée par ngrok (tu peux l'afficher depuis server.py)
NGROK_URL = "ws://URL_NGROK_ICI"

async def send_draw_event(websocket):
    """Simule un dessin (en vrai, il faudrait envoyer des coordonnées de dessin)"""
    while True:
        input("Appuie sur Entrée pour envoyer un dessin (simulation)...")
        draw_data = {"type": "draw", "data": "ligne_1"}
        await websocket.send(json.dumps(draw_data))

async def send_guess(websocket):
    """Permet au joueur d'envoyer un mot pour deviner"""
    while True:
        guess = input("Entre un mot pour deviner : ")
        await websocket.send(json.dumps({"type": "guess", "message": guess}))

async def receive_messages(websocket):
    """Écoute les messages du serveur"""
    async for message in websocket:
        data = json.loads(message)
        print(f"Message reçu : {data}")

async def main():
    async with websockets.connect(NGROK_URL) as websocket:
        asyncio.create_task(send_draw_event(websocket))
        asyncio.create_task(send_guess(websocket))
        await receive_messages(websocket)

asyncio.run(main())
