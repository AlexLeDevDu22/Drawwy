import asyncio, socketio, threading, time, tools

def start_connexion():
        try:

            if not asyncio.run(tools.test_server()):# start the serv
                
                import server
                server.stop_server()
                server=server
                
                server_thread = threading.Thread(target=server.start_server, daemon=True)
                server_thread.start()

                while not server.server_running:
                    time.sleep(0.1)

            asyncio.run(handle_connection_client())# start the web connection

        except KeyboardInterrupt:
            pass

async def handle_connection_client():
    sio = socketio.AsyncClient(logger=True, engineio_logger=True)

    @sio.event
    async def connect(): #joining the game
        print("joined")
        await sio.emit("join", {"type": "join", "pseudo": "Al", "avatar": {"type": "emoji", "emoji": "😁"}})

    @sio.event
    async def disconnect():
        print("Déconnecté du serveur WebSocket.")


    
    await sio.connect(f"https://vital-mastiff-publicly.ngrok-free.app")

    # Boucle pour écouter et réagir aux messages
    await sio.wait()

start_connexion()