import asyncio
import json
import websockets
import ngrok
import threading
import os
import yaml
from datetime import datetime
import sentences
import tools
from dotenv import load_dotenv

# Charger config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Charger le token ngrok depuis .env
load_dotenv()
ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
ngrok_domain = os.getenv("NGROK_DOMAIN")

ngrok.set_auth_token(ngrok_token)

#* game variables
global canvas,players, guess_list, drawer_id, sentences_list
players = []
drawer_id = 0  # ID du joueur actif
guess_list=[]

sentences_list=[sentences.new_sentence()]

last_game_start=None

# Création du tableau de dessin tous blancs
canvas = [[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]

def start_server():

    # Expose le serveur WebSocket sur le port 8765
    public_url = ngrok.connect(8765, domain=ngrok_domain)
    print(f"Serveur WebSocket accessible à : {public_url}")

    # =================== Données du serveur =================== #

    global server_started
    server_started=True # server is ready

    async def send_update(frames=None, new_message=None, new_game=False):
        """Envoie les mises à jour de l'état du jeu à tous les joueurs."""
        
        state = {
            "type": "update",
            "players": [{"id": p["id"], "pseudo": p["pseudo"], "points": p["points"], "found":p["found"]} for p in players],#players datas without ws key
            "frames": frames,
            "drawer_id": drawer_id,
            "new_message":new_message,
            "sentence":sentences_list[-1],
            "found":False,
            "new_game":last_game_start.isoformat() if new_game else False
        }
        await broadcast(json.dumps(state))

async def broadcast(message):
    """Envoie un message à tous les joueurs connectés."""
    try:
        for player in players:
            await player["ws"].send(message)
                
    except websockets.exceptions.ConnectionClosedError:
        print("Un joueur s'est déconnecté.")
        players[:] = [p for p in players if p["ws"] != player["ws"]]
        await broadcast(message)

    async def handle_connection_server(websocket):  # Correction ici
        global canvas, guess_list, drawer_id, sentences_list, last_game_start
        try:
            # Attente du pseudo du joueur
            data = json.loads(await websocket.recv())

        if data["type"] == "join": #! JOINING
            pseudo = data["pseudo"]
            player_id = 0 if players==[] else players[-1]["id"] + 1 # ID unique
            new_player = {
                "id": player_id,
                "pseudo": pseudo,
                "points": 0,
                "found":False,
                "ws": websocket
            }
            players.append(new_player)
            

                # Envoyer l'ID du joueur et l'état initial du jeu
                await websocket.send(json.dumps({
                    "type": "welcome",
                    "id": player_id,
                    "canvas": canvas,
                    "messages":guess_list,
                    "new_game":last_game_start.isoformat() if last_game_start else False,
                }))

            if len(players)==2:
                last_game_start=datetime.now()
                await send_update(new_game=True)# Envoyer une mise à jour à tous
            else:
                await send_update()

        async for message in websocket:
            data = json.loads(message)

                if data["type"] == "draw": #! DRAW
                    # Mise à jour du dessin
                    canvas=tools.update_canva_by_frames(data["frames"], canvas)
                    await send_update(data["frames"])

                elif data["type"] == "guess": #! GUESS
                    list_found=[]
                    succeed=False
                    for i,player in enumerate(players): #found the player
                        if player["id"] == data["player_id"]:
                            if player["id"]==drawer_id:
                                mess={"guess":data["guess"], "player_id":player["id"],"pseudo":player["pseudo"], "succeed":False}
                            else:
                                succeed=tools.check_sentences(sentences_list[-1], data["guess"])
                                if succeed:
                                    if not player["found"]:
                                        players[i]["points"] += int((data["remaining_time"]/config["game_duration"])*len(players) *config["points_per_found"])
                                    players[i]["found"] = True
                                    
                                    for j in range(len(players)):
                                        if players[j]["id"] == drawer_id:
                                            players[j]["points"] += config["points_per_found"]
                                            break
                                mess={"guess":data["guess"], "player_id":player["id"],"pseudo":player["pseudo"],"points":player["points"], "succeed":succeed}
                        
                        if player["id"] != drawer_id:
                            list_found.append(player["found"])
                            
                        
                    guess_list.append(mess)
                    
                    new_game=False
                    if all(list_found):
                        new_game=True
                        last_game_start=datetime.now()
                        
                        sentences_list.append(sentences.new_sentence())
                        
                        for player in players:
                            player["found"]=False
                        for i in range(len(players)):
                            if int(players[i]["id"]) == int(drawer_id):
                                drawer_id = players[(i+1)%len(players)]["id"]
                                break
                        
                        canvas = [[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]
                        guess_list=[]

                    await send_update(new_message=mess, new_game=new_game)
                        
                elif data["type"] == "game_finished":
                    for player in players:
                        player["found"]=False
                    for i in range(len(players)):
                        if int(players[i]["id"]) == int(drawer_id):
                            drawer_id = players[(i+1)%len(players)]["id"]
                            break
                        
                    sentences_list.append(sentences.new_sentence())
                    
                    canvas = [[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]
                    guess_list=[]
                    
                    last_game_start=datetime.now()
                    print("fini", last_game_start)

                await send_update(new_game=True)

    except websockets.exceptions.ConnectionClosedOK or websockets.exceptions.ConnectionClosedError:
        print("Un joueur s'est déconnecté.")
        players[:] = [p for p in players if p["ws"] != websocket]
        await send_update()

def start_server():
    """Démarre le serveur WebSocket et Ngrok."""
    global server_stop_event
    global server

    print("Démarrage du serveur...")
    ngrok.connect(8765, domain=ngrok_domain)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(start_async_server())
    except asyncio.CancelledError:
        print("Serveur arrêté.")

def stop_server():
    """Arrête proprement le serveur WebSocket et Ngrok."""
    global server

    # Déclencher l'événement d'arrêt
    server_stop_event.set()

    # Arrêter WebSocket proprement
    if server:
        server.close()

    # Déconnecter Ngrok
    ngrok.disconnect()

    print("Serveur arrêté avec succès.")
