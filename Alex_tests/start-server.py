from pyngrok import ngrok
import os
from dotenv import load_dotenv

load_dotenv()

ngrok_token = os.getenv("NGROK_AUTH_TOKEN")

# Remplace par ton token ngrok que tu trouves dans ton tableau de bord ngrok
ngrok.set_auth_token(ngrok_token)

# Ouvre un tunnel sur le port de ton choix (par exemple le port 8765 pour WebSocket)
public_url = ngrok.connect(8765, domain="vital-mastiff-publicly.ngrok-free.app")

print(f"Ton serveur est exposé ici : {public_url}")

# Tu peux maintenant utiliser cette URL publique pour ton jeu
# Exemple d'un serveur WebSocket avec websockets
import websockets
import asyncio

async def handler(websocket, path):
    await websocket.send("Hello, Client!")

async def main():
    start_server = websockets.serve(handler, "localhost", 8765)
    await start_server
    print(f"Serveur en écoute sur {public_url}")
    await asyncio.Future()  # Bloque l'exécution pour garder le serveur en fonctionnement

# Lance le serveur
asyncio.run(main())
