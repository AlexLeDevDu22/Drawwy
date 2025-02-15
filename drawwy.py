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

        # Recevoir les mises à jour et dessiner si c'est son tour
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "welcome":
                gameVar.CANVAS=data["canvas"]
                gameVar.PLAYER_ID=data["id"]
                gameVar.MESSAGES=data["messages"]
                gameVar.CURRENT_SENTENCE=data["sentence"]
            else:
                gameVar.PLAYERS=data["players"]
                gameVar.CURRENT_SENTENCE=data["sentence"]
                gameVar.FOUND=data["found"]
                if data["new_message"]:
                    gameVar.MESSAGES.append(data["new_message"])
                if data["frames"]:
                    threading.Thread(target=update_canva_by_frames, args=(data["frames"])).start() # update canvas in realtime
                    
def update_canva_by_frames(frames):
    for frame in frames:#draw
        if "color" in frame.keys():
            current_drawing_color, current_drawing_radius=frame["color"],frame["radius"]
        if "radius" in frame.keys():
            current_drawing_radius=frame["radius"]
        
        gameVar.CANVAS=tools.draw_canvas(CANVAS, frame["x"], frame["y"], current_drawing_color, current_drawing_radius)
        time.sleep(frame["period"])

async def send_message(websocket, message):
    await websocket.send({"type":"guess","player_id":PLAYER_ID, "guess":message})

async def websocket_draw(websocket):
    await websocket.send({"type":"draw","period":0.1,"frames":[
                                                            {"x":0,"y":0,"color":"#000000","width":2},
                                                            {"x":2,"y":1},
                                                            {"x":0,"y":0,"color":"#220000"},
                                                            {"x":2,"y":1},
                                                            {"x":0,"y":0,"width":3},
                                                            {"x":2,"y":1}
                                                            ]
    })

is_server=not asyncio.run(test_server())

if is_server:
    import server
    
    connection=threading.Thread(target=server.start_server)
    connection.start()# start the serv
    
    PSEUDO = pages.input_pseudo()

    while not server.server_started:
        time.sleep(0.1)
else:
    PSEUDO = pages.input_pseudo()

threading.Thread(target=lambda: asyncio.run(handle_connection_client()), daemon=True).start()# start the web connection

#* here the UI with game variables

pages.gamePage()

pygame.quit()#for not crash
if is_server:
    connection.stop()