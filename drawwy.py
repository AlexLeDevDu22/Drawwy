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

async def test_server():
    try:
        async with websockets.connect("wss://"+NGROK_DOMAIN) as ws:
            return True
    except:
        return False
    

async def handle_connection_client():
    global PLAYER_ID, PSEUDO, PLAYERS, CURRENT_DRAWER, SCORE, CURRENT_SENTENCE, MESSAGES, CANVAS

    async with websockets.connect("wss://"+NGROK_DOMAIN) as websocket:
        # Demander un pseudo et s'enregistrer
        
        await websocket.send(json.dumps({"type": "join", "pseudo": PSEUDO}))
        
        gameVar.WS=websocket

        # Recevoir les mises à jour et dessiner si c'est son tour
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "welcome":
                gameVar.CANVAS=data["canvas"]
                gameVar.PLAYER_ID=data["id"]
            else:
                gameVar.PLAYERS=data["players"]
                gameVar.CURRENT_SENTENCE=data["sentence"]
                gameVar.CURRENT_DRAWER=data["drawer_id"]
                if data["new_message"] and data["new_message"]["player_id"] != gameVar.PLAYER_ID:
                    gameVar.MESSAGES.append(data["new_message"])
                    if data["new_message"]["player_id"] == gameVar.PLAYER_ID and data["new_message"]["succeed"]:
                        gameVar.FOUND=True
                if data["frames"] and gameVar.PLAYER_ID != gameVar.CURRENT_DRAWER: #new pixels and not the drawer
                    threading.Thread(target=tools.update_canva_by_frames, kwargs={"frames":data["frames"]}).start() # update canvas in realtime

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

pages.gamePage()

if is_server:
    server.stop_server()
    time.sleep(0.1)
os._exit(0) # kill threads