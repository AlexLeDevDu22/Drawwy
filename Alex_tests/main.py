import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
import threading
import tools

load_dotenv()
ngrok_domain = os.getenv("NGROK_DOMAIN")

async def test_server():
    try:
        async with websockets.connect("wss://"+ngrok_domain) as ws:
            return True
    except:
        return False
    
async def handle_connection_client(pseudo):
    async with websockets.connect("wss://"+ngrok_domain) as websocket:
        # Demander un pseudo et s'enregistrer
        
        await websocket.send(json.dumps({"type": "join", "pseudo": pseudo}))

        # Recevoir les mises à jour et dessiner si c'est son tour
        async for message in websocket:
            data = json.loads(message)
            
            #print(data)
                
            for row in data["canvas"]:
                print("".join(["⬜" if x is None else "⬛" for x in row]))
                
async def send_message(websocket, message):
    await websocket.send({"type":"guess", "sentence":message})

async def websocket_draw(websocket, message):#TODO send draw
    await websocket.send({"type":"draw","period":0.1,"frames":[
                                                            {"x":0,"y":0,"color":"#000000","width":2},
                                                            {"x":2,"y":1},
                                                            {"x":0,"y":0,"color":"#220000"},
                                                            {"x":2,"y":1},
                                                            {"x":0,"y":0,"width":3},
                                                            {"x":2,"y":1}
                                                            ]
    })


PSEUDO="pseudoBoy"

is_server=not asyncio.run(test_server())

print(is_server)

if is_server:
    import server
    
    threading.Thread(target=server.start_server).start()

    while not server.server_started:
        pass

asyncio.run(handle_connection_client(PSEUDO))
