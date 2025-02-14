import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import threading

load_dotenv()
ngrok_domain = os.getenv("NGROK_DOMAIN")

async def test_server():
    try:
        async with websockets.connect("ws://localhost:8765") as ws:
            return True
    except:
        return False
    
async def handle_connection_client(pseudo):
    async with websockets.connect("wss://"+ngrok_domain) as websocket:
        # Demander un pseudo et s'enregistrer
        
        await websocket.send(json.dumps({"type": "join", "pseudo": pseudo}))

        # Recevoir les mises à jour et dessiner si c'est son tour
        print(websocket)
        async for message in websocket:
            data = json.loads(message)
            
            print(data)
            
            if data["type"] == "welcome":
                print(f"🎮 Connecté avec l'ID {data['id']}")
                print(f"👥 Joueurs actuels : {[p['pseudo'] for p in data['players']]}")
            
            elif data["type"] == "update":
                print(f"📜 Mise à jour : {len(data['players'])} joueurs, Tour : {data['turn']}")
                print(f"🎨 Canvas mis à jour.")

is_server=not asyncio.run(test_server())

if is_server:
    import server
    
    threading.Thread(target=server.start_server).start()
    
pseudo = input("Entrez votre pseudo : ")

while not server.server_started:
    asyncio.run(handle_connection_client(pseudo))
