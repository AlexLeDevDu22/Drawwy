import socketio, server, threading, asyncio, time

threading.Thread(target=server.start_server, daemon=True).start()

while not server.server_running:
    time.sleep(0.1)

NGROK_DOMAIN = "vital-mastiff-publicly.ngrok-free.app"

sio = socketio.AsyncClient(logger=True, engineio_logger=True)

async def handle_connection_client():
    @sio.event
    async def connect():
        print("Connecté au serveur WebSocket.")
        await sio.emit("join", {"type": "join", "pseudo": "Al", "avatar": {"type": "emoji", "emoji": "👋", "color": [255, 0, 0]}})
    
    @sio.event
    async def disconnect():
        print("Déconnecté du serveur WebSocket.")
    
    try:
        await sio.connect(f"https://{NGROK_DOMAIN}")
        await sio.wait()  # Bloque ici jusqu'à interruption
    except asyncio.CancelledError:
        print("Connexion interrompue proprement.")
    except Exception as e:
        print(f"Erreur: {e}")

def start_connection(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(handle_connection_client())

def stop_connection(loop):
    for task in asyncio.all_tasks(loop):
        task.cancel()  # Annule toutes les tâches en cours
    loop.stop()  # Arrête explicitement la boucle

# Crée une boucle dédiée pour gérer async
loop = asyncio.new_event_loop()
connection_thread = threading.Thread(target=start_connection, args=(loop,), daemon=True)
connection_thread.start()

# Attendre 10 secondes avant d'interrompre
time.sleep(10)
print("Fermeture de la connexion...")
stop_connection(loop)