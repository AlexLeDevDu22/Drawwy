import threading
import launcher
launch_page=threading.Thread(target=launcher.launcher)
launch_page.start()

import pages
import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import tools
import time
import gameVar
import yaml
from datetime import datetime

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

async def test_server():
    try:
        async with websockets.connect("wss://"+NGROK_DOMAIN) as ws:
            return True
    except:
        return False
    

async def handle_connection_client():
    global gamePage

    async with websockets.connect("wss://"+NGROK_DOMAIN) as websocket:
        # Demander un pseudo et s'enregistrer
        
        await websocket.send(json.dumps({"type": "join", "pseudo": PSEUDO}))
        
        gameVar.WS=websocket

        # Recevoir les mises à jour et dessiner si c'est son tour
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "welcome":
                gameVar.ALL_FRAMES=data["all_frames"]
                tools.update_canva_by_frames(gameVar.ALL_FRAMES)
                gameVar.PLAYER_ID=data["id"]
                gameVar.MESSAGES=data["messages"]
            else:
                if data["new_game"]:
                    #save draw
                    if gameVar.PLAYER_ID == gameVar.CURRENT_DRAWER and gameVar.CANVAS and gameVar.CANVAS!=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]: #save your draw
                        tools.save_bmp(gameVar.CANVAS, f"your_best_draws/{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.bmp")
            
                    gameVar.CANVAS=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])] #reset canvas
                    gameVar.FOUND=False
                    gameVar.MESSAGES=[]
                    gameVar.GAMESTART=datetime.fromisoformat(data["new_game"])
                    
                gameVar.PLAYERS=data["players"]
                gameVar.CURRENT_SENTENCE=data["sentence"]
                gameVar.CURRENT_DRAWER=data["drawer_id"]
                if data["new_message"]:
                    if data["new_message"]["player_id"] == gameVar.PLAYER_ID:
                        gameVar.MESSAGES=gameVar.MESSAGES[:-1]
                    gameVar.MESSAGES.append(data["new_message"])
                    if data["new_message"]["player_id"] == gameVar.PLAYER_ID and data["new_message"]["succeed"]:
                        gameVar.FOUND=True
                if data["frames"] and gameVar.PLAYER_ID != gameVar.CURRENT_DRAWER: #new pixels and not the drawer
                    threading.Thread(target=tools.update_canva_by_frames, kwargs={"frames":data["frames"]}).start() # update canvas in realtime
                if data["roll_back"]:
                    gameVar.ROLL_BACK=data["roll_back"]
                    tools.update_canva_by_frames(gameVar.ALL_FRAMES, reset=True, delay=False)

load_dotenv()
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

is_server=not asyncio.run(test_server())

if is_server:
    # start the serv
    import server
    
    threading.Thread(target=server.start_server).start()
    
    launcher.connected=True
    launch_page.join()
    PSEUDO = pages.input_pseudo()

    while not server.server_started:
        time.sleep(0.1)
else:
    launcher.connected=True
    launch_page.join()
    PSEUDO = pages.input_pseudo()

threading.Thread(target=lambda: asyncio.run(handle_connection_client()),daemon=True).start()# start the web connection

gamePage=pages.gamePage()

if is_server:
    server.stop_server()
    time.sleep(0.1)
os._exit(0) # kill threads