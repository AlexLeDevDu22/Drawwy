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
<<<<<<< HEAD
                gameVar.ALL_FRAMES=data["all_frames"]
                tools.update_canva_by_frames(gameVar.ALL_FRAMES)
=======
                gameVar.ALL_FRAMES+=data["all_frames"]
                tools.update_canva_by_frames(data["all_frames"], delay=False)
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
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

                if data["new_game"]:
                    #save draw
                    if gameVar.PLAYER_ID == gameVar.CURRENT_DRAWER and gameVar.CANVAS and gameVar.CANVAS!=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])]: #save your draw
                        tools.save_canvas(gameVar.CANVAS, f"your_best_draws/{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.bmp", gameVar.CURRENT_SENTENCE)
            
                    gameVar.CANVAS=[[None for _ in range(config["canvas_width"])] for _ in range(config["canvas_height"])] #reset canvas
                    gameVar.ALL_FRAMES=[]
                    gameVar.FOUND=False
                    gameVar.MESSAGES.append("Nouvelle partie ! C'est le tour de "+[p["pseudo"] for p in gameVar.PLAYERS if p["id"]==gameVar.CURRENT_DRAWER][0])
                    gameVar.GAMESTART=datetime.fromisoformat(data["new_game"])
                    
                if data["new_message"]:
                    print(gameVar.MESSAGES)
                    if data["new_message"]["player_id"] == gameVar.PLAYER_ID:
                        gameVar.MESSAGES=gameVar.MESSAGES[:-1]
                    print(gameVar.MESSAGES)
                    gameVar.MESSAGES.append(data["new_message"])
                    print(gameVar.MESSAGES)
                    
                    if data["new_message"]["player_id"] == gameVar.PLAYER_ID and data["new_message"]["succeed"]:
                        gameVar.FOUND=True
                if data["frames"] and gameVar.PLAYER_ID != gameVar.CURRENT_DRAWER: #new pixels and not the drawer
                    gameVar.ALL_FRAMES=tools.split_steps_by_roll_back(gameVar.ALL_FRAMES, gameVar.ROLL_BACK)[0]
                    gameVar.ROLL_BACK=0

                    threading.Thread(target=tools.update_canva_by_frames, kwargs={"frames":data["frames"]}).start() # update canvas in realtime
<<<<<<< HEAD
                if data["roll_back"]:
                    gameVar.ROLL_BACK=data["roll_back"]
                    tools.update_canva_by_frames(gameVar.ALL_FRAMES, reset=True, delay=False)
=======

                    num_steps=0
                    for frame in gameVar.ALL_FRAMES:
                        if frame["type"] in ["new_step", "shape"]:
                            num_steps+=1
                    gameVar.STEP_NUM=num_steps

                    print("\n \n", gameVar.ALL_FRAMES)
                    print("\n rollbacks:", gameVar.ROLL_BACK)
                    print("steps:", gameVar.STEP_NUM)
                if data["roll_back"]!=gameVar.ROLL_BACK and gameVar.PLAYER_ID != gameVar.CURRENT_DRAWER:
                    gameVar.ROLL_BACK=data["roll_back"]
                    tools.update_canva_by_frames(gameVar.ALL_FRAMES, reset=True, delay=False)

                    print("\n \n", gameVar.ALL_FRAMES)

                    print("\n rollbacks:", gameVar.ROLL_BACK)
                    print("steps:", gameVar.STEP_NUM)
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf

load_dotenv()
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

if not tools.is_connected():
    raise "Désolé, une connexion internet est requise."

is_server=not asyncio.run(tools.test_server())

try:
    if is_server:
        # start the serv
        import server
        
        server_thread = threading.Thread(target=server.start_server, daemon=True)
        server_thread.start()

        launcher.connected=True
        launch_page.join()
        PSEUDO = pages.input_pseudo()

        while not server.server:
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

<<<<<<< HEAD
threading.Thread(target=lambda: asyncio.run(handle_connection_client()),daemon=True).start()# start the web connection

gamePage=pages.gamePage()

if is_server:
    server.stop_server()
    time.sleep(0.1)
os._exit(0) # kill threads
=======
except KeyboardInterrupt:
    if is_server:
        server.stop_server()
        time.sleep(0.1)
    os._exit(0)
>>>>>>> 3e91ce9893a21cb51c00c03e06d82dd226e02bdf
