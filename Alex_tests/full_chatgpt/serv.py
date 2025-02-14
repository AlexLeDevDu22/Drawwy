import asyncio
import json
import websockets
from pyngrok import ngrok
from dotenv import load_dotenv
import os

# Charger le token ngrok depuis .env
load_dotenv()
ngrok_token = os.getenv("NGROK_AUTH_TOKEN")

# Vérification
if not ngrok_token:
    raise ValueError("Token NGROK manquant dans le fichier .env !")

ngrok.set_auth_token(ngrok_token)

# Expose le serveur WebSocket sur le port 8765
public_url = ngrok.connect(8765, "tcp")
print(f"Serveur WebSocket accessible à : {public_url}")

# Liste des joueurs connectés
connected_players = set()
drawer = None  # Le joueur qui dessine
current_word = "pomme"  # Mot à deviner (tu peux générer un mot aléatoire)

async def handle_connection(websocket, path):
    global drawer, current_word

    # Ajouter le joueur à la liste
    connected_players.add(websocket)
    print(f"Nouveau joueur connecté. Total : {len(connected_players)} joueurs.")

    if drawer is None:
        drawer = websocket  # Premier joueur devient le dessinateur

    try:
        async for message in websocket:
            data = json.loads(message)

            if data["type"] == "draw":
                # Relayer le dessin à tous les autres joueurs
                for player in connected_players:
                    if player != websocket:
                        await player.send(json.dumps(data))

            elif data["type"] == "guess":
                guess = data["message"].lower()
                if guess == current_word.lower():
                    for player in connected_players:
                        await player.send(json.dumps({"type": "correct", "message": f"Le mot '{current_word}' a été trouvé !"}))
                    
                    # Nouveau mot et changement de dessinateur
                    drawer = next(iter(connected_players - {drawer}), None)  # Prochain joueur
                    current_word = "chien"  # Générer un nouveau mot
                    await drawer.send(json.dumps({"type": "draw_turn", "message": "C'est ton tour de dessiner !"}))
    
    except websockets.exceptions.ConnectionClosed:
        print("Un joueur s'est déconnecté.")
        connected_players.remove(websocket)

# Lancer le serveur WebSocket
async def main():
    async with websockets.serve(handle_connection, "localhost", 8765):
        await asyncio.Future()  # Garde le serveur en fonctionnement

asyncio.run(main())
