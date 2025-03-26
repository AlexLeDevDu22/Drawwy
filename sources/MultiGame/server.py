from shared.utils.data_manager import *

import os
from datetime import datetime
import MultiGame.utils.sentences as sentences
import MultiGame.utils.tools as tools
import shutil
from aiohttp import web
import asyncio
import socket
from pyngrok import ngrok

server_name = None

# Variables pour le serveur
server_started = False
http_tunnel = None
flask_thread = None

port = None

# Stocke les WebSockets
app = None
websockets = set()

loop = None

async def handle_websocket(request):
    global ws

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # Ajouter le WebSocket à la liste
    websockets.add(ws)

    try: 
        async for message in ws:
            data = message.json()

            if data["header"] == "join":
                await handle_join(data, ws)
            elif data["header"] == "new_message":
                if data["type"] == "guess":
                    await handle_guess(data)
                elif data["type"] == "emote":
                    await handle_emote(data)
            elif data["header"] == "roll_back":
                await handle_roll_back(data, ws)
            elif data["header"] == "draw":
                await handle_draw(data)
            elif data["header"] == "game_finished":
                await handle_new_game(data)

    except Exception as e:
        print(f"Error handling WebSocket: {e}")
    finally:
        # Enlever le WebSocket de la liste
        await handle_disconnect(ws)
        websockets.remove(ws)
        return ws

async def handle_disconnect(ws):
    global players
    if players:
        # Trouver le joueur qui s'est déconnecté
        for i, player in enumerate(players):
            print(i, player["ws"], ws)
            if player["ws"] == ws:
                print(f"Joueur {player['pseudo']} déconnecté")
                players.pop(i)
                break

        if player["avatar"]["type"] == "matrix" and os.path.exists(
                f"sources/MultiGame/web/temp-assets/avatars/{player['pid']}.bmp"):
            os.remove(f"sources/MultiGame/web/temp-assets/avatars/{player["pid"]}.bmp")

        # Envoyer la mise à jour des joueurs

        await broadcast({
            "header": "player_disconnected",
            "pid": player["pid"],
            "pseudo": player["pseudo"]
        })


async def handle_join(data, ws):
    global players, last_game_start

    if len(players) > 0:
        pid = players[-1]["pid"] + 1
    else:
        pid = 0

    # Ajouter le joueur à la liste
    players.append({
        "pid": pid,
        "pseudo": data["pseudo"],
        "avatar": data["avatar"],
        "points": 0,
        "found": False,
        "ws": ws
    })

    # Envoyer l'ID du joueur et l'état initial du jeu
    await broadcast({
            "header": "welcome",
            "pid": pid,
            "players": [{"pid": p["pid"],
                        "pseudo": p["pseudo"],
                        "avatar": p["avatar"],
                        "points": p["points"],
                        "found": p["found"]} for p in players],
            "sentence": sentences_list[-1],
            "drawer_id": drawer_id,
            "all_frames": all_frames,
            "messages": guess_list,
            "new_game": last_game_start.isoformat() if len(players) > 1 and last_game_start else False,
            "roll_back": roll_back},
          target_pid = pid
          )

    # enregistrer l'avatar
    if data["avatar"]["type"] == "matrix":
        tools.save_canvas(data["avatar"]["matrix"],
                          "sources/MultiGame/web/temp-assets/avatars/" + str(pid) + ".bmp",
                          sentences_list[-1],
                          False)

    await broadcast({
        "header": "new_player",
        "pid": pid,
        "pseudo": data["pseudo"],
        "avatar": data["avatar"],
        "points": 0,
        "found": False
    }, skip_id=pid)

    if len(players) == 2:
        await handle_new_game()


async def handle_new_game(data=None):
    global last_game_start, players, drawer_id, sentences_list, guess_list, all_frames, roll_back

    guess_list = []
    all_frames = []
    roll_back = 0
    last_game_start = datetime.now()
    sentences_list.append(sentences.new_sentence())

    for i in range(len(players)):
        players[i]["found"] = False

    # Changer de dessinateur
    if drawer_id != -1:
        for i in range(len(players)):
            if int(players[i]["pid"]) == int(drawer_id):
                drawer_id = players[(i + 1) % len(players)]["pid"]
                break
    else:
        drawer_id = players[0]["pid"]

    await broadcast({
        "header": "new_game",
        "drawer_id": drawer_id,
        "start_time": last_game_start.isoformat(),
        "new_sentence": sentences_list[-1]
    })


async def handle_draw(data):
    global all_frames

    all_frames += data["frames"]

    await broadcast(data, skip_id=drawer_id)


async def handle_roll_back(data, ws):
    global roll_back

    roll_back = data["roll_back"]

    await broadcast(data, skip_id=drawer_id)


async def handle_guess(message):
    global players, drawer_id, guess_list, sentences_list

    list_found = []
    succeed = False

    message["succeed"] = False

    for i, player in enumerate(players):
        if message["pid"] == player["pid"] and player["pid"] != drawer_id:
            succeed = tools.check_sentences(
                sentences_list[-1], message["message"])
            if succeed and not player["found"]:
                message["succeed"] = True
                # point au founder
                founder_points = int(
                    (message["remaining_time"] /
                        CONFIG["game_duration"]) *
                    len(players) *
                    CONFIG["points_per_found"])
                players[i]["points"] += founder_points
                players[i]["found"] = True

                # Donner des points au dessinateur
                drawer_points = CONFIG["points_per_found"]
                for j in range(len(players)):
                    if players[j]["pid"] == drawer_id:
                        players[j]["points"] += drawer_points
                        break

                message["new_points"] = [{"pid": player["pid"], "points": founder_points}, {
                    "pid": drawer_id, "points": drawer_points}]

        if player["pid"] != drawer_id:
            list_found.append(player["found"])

    guess_list.append(message)

    await broadcast(message)

    # Vérifier si tous les joueurs ont trouvé
    if len(players) > 1 and all(list_found):
        await handle_new_game()

async def handle_emote(message):

    message["header"] = "new_message"

    if not os.path.exists(
        "sources/MultiGame/web/temp-assets/emotes/" +
            message["emote_path"]):
        if os.path.exists(
            "data/shop/emotes_assets/" +
                message["emote_path"]):
            shutil.copyfile(
                "data/shop/emotes_assets/" +
                message["emote_path"],
                "sources/MultiGame/web/temp-assets/emotes/" +
                message["emote_path"])

    await broadcast(message)

async def broadcast(message, skip_id=None, target_pid=None):
    """Envoie un message à tous les WebSockets connectés."""
    
    for player in players:
        if player["pid"] != skip_id and (target_pid is None or player["pid"] == target_pid):
            await player["ws"].send_json(message)

def get_num_players(request):
    return web.json_response({"num_players": len(players)})

async def redirect_to_index(request):
    """Redirige vers index.html"""
    raise web.HTTPFound("/index.html") 
    
async def start_web():
    global app, port

    app = web.Application()
    
    # Route WebSocket
    app.router.add_get("/ws", handle_websocket)

    app.router.add_get("/", redirect_to_index) 

    app.router.add_static("/", "sources/MultiGame/web", show_index=True)

    app.router.add_get("/num_players", get_num_players)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


def get_free_port():
    """Retourne un port libre utilisable."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # Bind sur un port aléatoire libre
        return s.getsockname()[1]  # Retourne le numéro du port


def start_server(serv_name):
    """Démarre le serveur HTTP + WebSocket dans un thread."""
    global ngrok, server_started, server_name, loop, players, drawer_id, guess_list, sentences_list, last_game_start, all_frames, roll_back, port

    # Variables du jeu
    players = []
    drawer_id = -1
    guess_list = []
    sentences_list = [sentences.new_sentence()]
    last_game_start = None
    all_frames = []
    roll_back = 0

    server_name = serv_name

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Lancer Ngrok
    ngrok.kill()
    ngrok.set_auth_token(CONFIG["servers"][server_name]["auth_token"])
    port=get_free_port()
    ngrok.connect(port, domain=CONFIG["servers"][server_name]["domain"])

    loop.run_until_complete(start_web())  # Exécuter le serveur
    server_started = True
    loop.run_forever()

def stop_server():
    """Ferme proprement le serveur WebSocket, HTTP et Ngrok."""
    global app, websockets, server_started, server_name, loop, ngrok

    if not server_started or not loop:
        return

    print("🛑 Arrêt du serveur...")

    async def shutdown():
        global server_started, server_name, ngrok
        # Fermer toutes les WebSockets
        for ws in list(websockets):
            await ws.close()

        # Fermer l'application web
        if app is not None:
            await app.shutdown()
            await app.cleanup()
        
        ngrok.disconnect(CONFIG["servers"][server_name]["domain"])

        server_started = False

        # Arrêter toutes les tâches restantes
        tasks = [t for t in asyncio.all_tasks(loop) if t is not asyncio.current_task()]
        [t.cancel() for t in tasks]  # Annuler les tâches actives

        loop.stop()
    asyncio.run_coroutine_threadsafe(shutdown(), loop)

# Fonction pour être compatible avec un import et un lancement direct
if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        stop_server(server_name)
