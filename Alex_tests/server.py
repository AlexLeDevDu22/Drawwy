import asyncio
import json
import websockets
from pyngrok import ngrok
from dotenv import load_dotenv
import os
from sentence_transformers import SentenceTransformer, util

server_started=False

def start_server():
    # Charger le token ngrok depuis .env
    load_dotenv()
    ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
    ngrok_domain = os.getenv("NGROK_DOMAIN")


    ngrok.set_auth_token(ngrok_token)

    # Expose le serveur WebSocket sur le port 8765
    public_url = ngrok.connect(8765, domain=ngrok_domain)
    print(f"Serveur WebSocket accessible à : {public_url}")
    server_started=True

    # =================== Données du serveur =================== #

    # Liste des joueurs (avec ID, pseudo, points)
    players = []
    player_turn = None  # ID du joueur actif

    # Création du tableau de dessin (100x100 pixels, tous blancs)
    canvas_size = 20  # Taille du canvas (20x20 pour le test)
    canvas = [[None for _ in range(canvas_size)] for _ in range(canvas_size)]

    async def send_update():
        """Envoie les mises à jour de l'état du jeu à tous les joueurs."""
        
        state = {
            "type": "update",
            "players": [{"id": p["id"], "pseudo": p["pseudo"], "points": p["points"]} for p in players],#players datas without ws key
            "canvas": canvas,
            "turn": player_turn
        }
        await broadcast(json.dumps(state))

    async def broadcast(message):
        """Envoie un message à tous les joueurs connectés."""
        for player in players:
            await player["ws"].send(message)

    async def handle_connection_server(websocket):  # Correction ici
        player_turn=None

        try:
            # Attente du pseudo du joueur
            message = await websocket.recv()
            data = json.loads(message)

            if data["type"] == "join":
                pseudo = data["pseudo"]
                player_id = 0 if players==[] else players[-1]["id"] + 1 # ID unique
                new_player = {
                    "id": player_id,
                    "pseudo": pseudo,
                    "points": 0,
                    "ws": websocket
                }
                players.append(new_player)

                # Définir le premier joueur comme dessinateur
                if player_turn is None:
                    player_turn = player_id
                    

                # Envoyer l'ID du joueur et l'état initial du jeu
                await websocket.send(json.dumps({
                    "type": "welcome",
                    "id": player_id,
                    "canvas": canvas,
                    "players": [{"id": p["id"], "pseudo": p["pseudo"], "points": p["points"]} for p in players],#players datas without ws key
                    "turn": player_turn
                }))

                # Envoyer une mise à jour à tous
                await send_update()

            async for message in websocket:
                data = json.loads(message)

                if data["type"] == "draw":
                    # Mise à jour du dessin
                    x, y, color = data["x"], data["y"], data["color"]
                    canvas[y][x] = color
                    await send_update()

                elif data["type"] == "guess":
                    # Vérification du mot (pas encore implémenté)
                    pass

        except websockets.exceptions.ConnectionClosed:
            print("Un joueur s'est déconnecté.")
            players[:] = [p for p in players if p["ws"] != websocket]
            await send_update()

    async def main():
        async with websockets.serve(handle_connection_server, "localhost", 8765):
            await asyncio.Future()

    asyncio.run(main())
    
    

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")  # Gère plusieurs langues

def sentences_checker(sentence1, sentence2):
    emb1 = model.encode(sentence1, convert_to_tensor=True)
    emb2 = model.encode(sentence2, convert_to_tensor=True)
    score = util.pytorch_cos_sim(emb1, emb2).item()
    return score