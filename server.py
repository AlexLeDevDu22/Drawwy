import asyncio
import json
import websockets
import ngrok
from dotenv import load_dotenv
import os
import tools
import yaml
from datetime import datetime

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

server_started=False

# Charger le token ngrok depuis .env
load_dotenv()
ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
ngrok_domain = os.getenv("NGROK_DOMAIN")

ngrok.set_auth_token(ngrok_token)

#* game variables
global canvas,players, guess_list, drawer_id, sentences
players = []
drawer_id = 0  # ID du joueur actif
guess_list=[]

sentences=[tools.get_random_sentence()]

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

    async def send_update(frames=None, new_message=None, only_drawer=False, new_game=False):
        """Envoie les mises à jour de l'état du jeu à tous les joueurs."""
        
        state = {
            "type": "update",
            "players": [{"id": p["id"], "pseudo": p["pseudo"], "points": p["points"], "found":p["found"]} for p in players],#players datas without ws key
            "frames": frames,
            "drawer_id": drawer_id,
            "new_message":new_message,
            "sentence":sentences[-1],
            "found":False,
            "new_game":last_game_start.isoformat() if new_game else False
        }
        await broadcast(json.dumps(state), only_drawer)

    async def broadcast(message, only_drawer):
        """Envoie un message à tous les joueurs connectés."""
        try:
            for player in players:
                if (not only_drawer) or player["id"] == drawer_id:
                    await player["ws"].send(message)
                    
        except websockets.exceptions.ConnectionClosedError:
            print("Un joueur s'est déconnecté.")
            players[:] = [p for p in players if p["ws"] != player["ws"]]
            await broadcast(message, only_drawer)

    async def handle_connection_server(websocket):  # Correction ici
        global canvas, guess_list, drawer_id, sentences, last_game_start
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
                    "new_game":last_game_start
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
                    for player in players: #found the player
                        if player["id"] == data["player_id"]:
                            #await send_update(new_message={"guess":data["guess"], "id":player["id"], "succeed":succeed})
                            succeed=tools.check_sentences(sentences[-1], data["guess"])
                            if succeed:
                                player["found"] = True
                                player["points"] += 2
                                
                                for i in len(players):
                                    if players[i]["id"] == drawer_id:
                                        players[i]["points"] -= 1
                                
                            if player["id"] != drawer_id:
                                list_found.append(player["found"])
                            
                                
                            mess={"guess":data["guess"], "player_id":player["id"],"pseudo":player["pseudo"], "succeed":succeed}
                            
                            
                    guess_list.append(mess)
                    
                    new_game=False
                    if all(list_found):
                        new_game=datetime.now()
                        last_game_start=new_game
                    
                    await send_update(new_message=mess, new_game=new_game)
                        
                elif data["type"] == "game_finished":
                    for player in players:
                        player["found"]=False
                    for i in range(len(players)):
                        if int(players[i]["id"]) == int(drawer_id):
                            drawer_id = players[(i+1)%len(players)]["id"]
                            break
                        
                    sentences.append(tools.get_random_sentence())
                    
                    canvas = [[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]
                    guess_list=[]

                    await send_update(new_game=True)

        except websockets.exceptions.ConnectionClosedOK:
            print("Un joueur s'est déconnecté.")
            players[:] = [p for p in players if p["ws"] != websocket]
            await send_update()
            

    async def main():
        async with websockets.serve(handle_connection_server, "localhost", 8765):
            await asyncio.Future()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())

    stop_server()

def stop_server():
    global ngrok_domain
    ngrok.disconnect(ngrok_domain)
    
stop_server()#close the serv if it already exists  doesn't work