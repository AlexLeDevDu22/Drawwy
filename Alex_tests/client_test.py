import asyncio
import json
import websockets
import random
from dotenv import load_dotenv
import os

load_dotenv()
ngrok_domain = os.getenv("NGROK_DOMAIN")


async def draw_pixel(websocket, player_id):
    """Simule le dessin en changeant des pixels au hasard."""
    while True:
        await asyncio.sleep(1)
        x, y = random.randint(0, 19), random.randint(0, 19)
        color = f"#{random.randint(0, 0xFFFFFF):06x}"  # Couleur aléatoire
        await websocket.send(json.dumps({"type": "draw", "x": x, "y": y, "color": color}))

async def receive_messages(websocket):
    """Affiche les messages du serveur."""
    async for message in websocket:
        data = json.loads(message)
        
        if data["type"] == "welcome":
            print(f"🎮 Connecté avec l'ID {data['id']}")
            print(f"👥 Joueurs actuels : {[p['pseudo'] for p in data['players']]}")
        
        elif data["type"] == "update":
            print(f"📜 Mise à jour : {len(data['players'])} joueurs, Tour : {data['turn']}")
            print(f"🎨 Canvas mis à jour.")

async def main():
    async with websockets.connect("wss://"+ngrok_domain) as websocket:
        # Demander un pseudo et s'enregistrer
        pseudo = input("Entrez votre pseudo : ")
        await websocket.send(json.dumps({"type": "join", "pseudo": pseudo}))

        # Recevoir les mises à jour et dessiner si c'est son tour
        asyncio.create_task(receive_messages(websocket))
        await draw_pixel(websocket, pseudo)

asyncio.run(main())
