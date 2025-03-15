import asyncio
import socketio
import threading
import MultiGame.utils.tools as tools
import os
from dotenv import load_dotenv
import time
import yaml
import json
from datetime import datetime

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

connection_loop=None

def start_connexion(MultiGameClass):
    try:

        if not asyncio.run(tools.test_server()):# start the serv
            
            import MultiGame.server as server
            threading.Thread(target=server.start_server, daemon=True).start()

            while not server.server_running:
                time.sleep(0.1)

        global connection_loop
        connection_loop=asyncio.new_event_loop()
        asyncio.set_event_loop(connection_loop)
        MultiGameClass.connection_loop.run_until_complete(handle_connection_client(MultiGameClass))
    except RuntimeError:
        print("connexion fermé")

async def handle_connection_client(MultiGame):

    load_dotenv()
    NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

    MultiGame.SIO = socketio.AsyncClient(logger=True, engineio_logger=True)
    @MultiGame.SIO.event
    async def connect(): #joining the game
        with open("data/players_data.json") as f:
            player_data = json.load(f)

        await MultiGame.SIO.emit("join", {"type": "join", "pseudo": player_data["pseudo"], "avatar": {"type": "matrix", "matrix": tools.load_bmp_to_matrix("assets/avatar.bmp")}})

    @MultiGame.SIO.event
    async def disconnect():
        print("Déconnecté du serveur WebSocket.")


    @MultiGame.SIO.on('welcome')
    async def welcome(data):
        MultiGame.connected=True
        MultiGame.ALL_FRAMES+=data["all_frames"]
        MultiGame.PLAYER_ID=data["id"]
        MultiGame.MESSAGES=data["messages"]
        MultiGame.PLAYERS=data["players"]
        MultiGame.CURRENT_SENTENCE=data["sentence"]
        MultiGame.CURRENT_DRAWER=data["drawer_id"]
        tools.update_canva_by_frames(MultiGame, data["all_frames"], delay=False)

    @MultiGame.SIO.on("new_player")
    async def new_player(data):
        MultiGame.PLAYERS.append(data)
        MultiGame.MESSAGES.append({"type":"system","message":data["pseudo"]+" viens de nous rejoindre!", "color": config["succeed_color"]})

    @MultiGame.SIO.on("player_disconnected")
    async def player_disconnected(data):
        for i in range(len(MultiGame.PLAYERS)):
            if MultiGame.PLAYERS[i]["id"]==data["pid"]:
                player=MultiGame.PLAYERS.pop(i)
                break

        MultiGame.MESSAGES.append({"type":"system","message":player["pseudo"]+" à quitté la partie.", "color": config["bad_color"]})

    @MultiGame.SIO.on("new_game")
    def new_game(data):
        #save draw
        if MultiGame.PLAYER_ID == MultiGame.CURRENT_DRAWER and MultiGame.CANVAS and MultiGame.CANVAS!=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]: #save your draw
            tools.save_canvas(MultiGame.CANVAS, f"assets/your_best_draws/{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.bmp", MultiGame.CURRENT_SENTENCE)

        MultiGame.CANVAS=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])] #reset canvas
        MultiGame.CURRENT_SENTENCE=data["new_sentence"]
        MultiGame.CURRENT_DRAWER=data["drawer_id"]
        MultiGame.MESSAGES=[{"type":"system","message":"Nouvelle partie ! C'est le tour de "+[p["pseudo"] for p in MultiGame.PLAYERS if p["id"]==MultiGame.CURRENT_DRAWER][0], "color": config["succeed_color"]}]
        MultiGame.ALL_FRAMES=[]
        MultiGame.FOUND=False
        MultiGame.GAMESTART=datetime.fromisoformat(data["start_time"])
        MultiGame.ROLL_BACK=0

    @MultiGame.SIO.on("draw")
    async def draw(frames):
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER: #not the drawer
            MultiGame.ALL_FRAMES=tools.split_steps_by_roll_back(MultiGame.ALL_FRAMES, MultiGame.ROLL_BACK)[0]
            MultiGame.ROLL_BACK=0

            threading.Thread(target=tools.update_canva_by_frames, kwargs={"MultiGame": MultiGame, "frames":frames}).start() # update canvas in realtime

            num_steps=0
            for frame in MultiGame.ALL_FRAMES:
                if frame["type"] == "new_step":
                    num_steps+=1
            MultiGame.STEP_NUM=num_steps


    @MultiGame.SIO.on("new_message")
    def new_message(guess):
        #ajouter à la liste de message
        if guess["pid"] == MultiGame.PLAYER_ID:
            MultiGame.MESSAGES=MultiGame.MESSAGES[:-1]
        MultiGame.MESSAGES.append(guess)
        
        #update found and points
        if guess["succeed"]:
            for i in range(len(MultiGame.PLAYERS)):
                if MultiGame.PLAYERS[i]["id"]==guess["pid"]:
                    MultiGame.PLAYERS[i]["found"]=True
        
            for e in guess["new_points"]:
                for i in range(len(MultiGame.PLAYERS)):
                    if MultiGame.PLAYERS[i]["id"]==e["pid"]:
                        MultiGame.PLAYERS[i]["points"]+=e["points"]


    @MultiGame.SIO.on("roll_back")
    async def roll_back(roll_back):
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:
            MultiGame.ROLL_BACK=roll_back
            tools.update_canva_by_frames(MultiGame, MultiGame.ALL_FRAMES, reset=True, delay=False)
            

    try:
        await MultiGame.SIO.connect(f"https://{NGROK_DOMAIN}")

        # Boucle pour écouter et réagir aux messages
        await MultiGame.SIO.wait()
    except asyncio.CancelledError:
        print("déconnecté du server")

def disconnect(MultiGame):
    global connection_loop
    MultiGame.SIO.disconnect()
    for task in asyncio.all_tasks(connection_loop):
        task.cancel()
    MultiGame.connection_loop.stop()
    if MultiGame.server:
        MultiGame.server.stop_server()
    MultiGame.connexion_thread.join()
    print("deco")