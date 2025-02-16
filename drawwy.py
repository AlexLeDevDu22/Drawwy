import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import threading
import pygame
import tools
import pages
import time
import gameVar

load_dotenv()
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

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
                if data["new_message"]:
                    gameVar.MESSAGES.append(data["new_message"])
                    if data["new_message"]["player_id"] == gameVar.PLAYER_ID and data["new_message"]["succeed"]:
                        gameVar.FOUND=True
                if data["frames"] and gameVar.PLAYER_ID != gameVar.CURRENT_DRAWER: #new pixels and not the drawer
                    threading.Thread(target=tools.update_canva_by_frames, kwargs={"frames":data["frames"]}).start() # update canvas in realtime


is_server=not asyncio.run(test_server())

if is_server:
    import server
    
    threading.Thread(target=server.start_server).start()# start the serv
    
    PSEUDO = pages.input_pseudo()

    while not server.server_started:
        time.sleep(0.1)
else:
    PSEUDO = pages.input_pseudo()

threading.Thread(target=lambda: asyncio.run(handle_connection_client()), daemon=True).start()# start the web connection

#* here the UI with game variables

pages.gamePage()

pygame.quit()#for not crash
os._exit(0) # for threads