import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import threading
import tools
import pygame
import pages

load_dotenv()
NGROK_DOMAIN = os.getenv("NGROK_DOMAIN")

async def test_server():
    try:
        async with websockets.connect("wss://"+NGROK_DOMAIN) as ws:
            return True
    except:
        return False
    
#! MAIN VARIABLES
PLAYER_ID=0
PSEUDO="pseudoBoy"
PLAYERS=[]
CURRENT_DRAWER=0
SCORE=0
CURRENT_SENTENCE=""
MESSAGES=[]
CANVAS=[]


async def handle_connection_client():
    async with websockets.connect("wss://"+NGROK_DOMAIN) as websocket:
        # Demander un pseudo et s'enregistrer
        
        await websocket.send(json.dumps({"type": "join", "pseudo": PSEUDO}))

        # Recevoir les mises à jour et dessiner si c'est son tour
        async for message in websocket:
            data = json.loads(message)
            
            print(data)
            
            if data["type"] == "welcome":
                CANVAS=data["canvas"]
                PLAYER_ID=data["id"]
                MESSAGES=data["messages"]
            else:
                PLAYERS=data["players"]
                CURRENT_SENTENCE=data["sentence"]
                if data["new_message"]:
                    MESSAGES.append(data["new_message"])
                if data["frames"]:
                    threading.Thread(target=update_canva_by_frames(), args=(data["frames"])).start() # update canvas in realtime
                    
def update_canva_by_frames(frames):
    for frame in frames:#draw
        if "color" in frame.keys():
            current_drawing_color, current_drawing_radius=frame["color"],frame["radius"]
        if "radius" in frame.keys():
            current_drawing_radius=frame["radius"]
        
        CANVAS=tools.draw_canvas(CANVAS, frame["x"], frame["y"], current_drawing_color, current_drawing_radius)

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
    
    threading.Thread(target=server.start_server).start()
    
pygame.init()
PSEUDO = pages.input_pseudo()

while not server.server_started and is_server:
    pass

asyncio.run(handle_connection_client())


#* here the UI with game variables