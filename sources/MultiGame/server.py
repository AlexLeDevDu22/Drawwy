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
    """
    Handle a WebSocket connection.

    This function is a callback that is called by aiohttp when a WebSocket connection is established. It
    sets up the WebSocket and adds it to the list of active WebSockets. It then listens for messages on
    the WebSocket and dispatches them to the appropriate handler function. If an error occurs, it prints
    the error and removes the WebSocket from the list of active WebSockets.

    Parameters:
    request (aiohttp.web.Request): The request that established the WebSocket connection

    Returns:
    aiohttp.web.WebSocketResponse: The WebSocketResponse object that was created
    """
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
                await handle_roll_back(data)
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
    """
    Handles the disconnection of a player.

    This function is called when a WebSocket connection is closed. It removes the player associated
    with the given WebSocket from the players list and performs necessary cleanup, such as removing
    the player's avatar file. It broadcasts a message to inform other players of the disconnection
    and starts a new game if the disconnected player was the current drawer.

    Parameters:
    ws (aiohttp.web.WebSocketResponse): The WebSocket connection of the player that disconnected.
    """

    global players
    if players:
        # Trouver le joueur qui s'est déconnecté
        for i, player in enumerate(players):
            if player["ws"] == ws:
                if player["avatar"]["type"] == "matrix" and os.path.exists(
                        f"sources/MultiGame/web/temp-assets/avatars/{player['pid']}.bmp"):
                    os.remove(
                        f"sources/MultiGame/web/temp-assets/avatars/{player["pid"]}.bmp")

                players.pop(i)
                break

        # Envoyer la mise à jour des joueurs

        await broadcast({
            "header": "player_disconnected",
            "pid": player["pid"],
            "pseudo": player["pseudo"]
        })

        if player["pid"] == drawer_pid:
            await handle_new_game()


async def handle_join(data, ws):
    """
    Handles a player joining the game.

    This function is called when a player joins the game. It adds the player to the players list
    and sends the player's ID and the initial game state to the player. It also saves the player's avatar
    if it is a matrix. It broadcasts a message to inform other players of the new player and starts
    a new game if there are two players.

    Parameters:
    data (dict): The data sent by the player when they joined.
    ws (aiohttp.web.WebSocketResponse): The WebSocket connection of the player that joined.
    """
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
        "drawer_pid": drawer_pid,
        "all_frames": all_frames,
        "messages": guess_list,
        "new_game": last_game_start.isoformat() if len(players) > 1 and last_game_start else False,
        "roll_back": roll_back},
        target_pid=pid
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
    """
    Starts a new game when a player joins.

    This function resets the game state: it clears the guess list, resets the frames list,
    sets the roll back to 0, starts a new timer, generates a new sentence, resets the points
    of all players and changes the drawer.

    Parameters:
    data (dict): The data sent by the player when they joined (not used).

    """
    global last_game_start, players, drawer_pid, sentences_list, guess_list, all_frames, roll_back

    guess_list = []
    all_frames = []
    roll_back = 0
    last_game_start = datetime.now()
    sentences_list.append(sentences.new_sentence())

    for i in range(len(players)):
        players[i]["found"] = False

    # Changer de dessinateur
    if drawer_pid != -1:
        for i in range(len(players)):
            if int(players[i]["pid"]) == int(drawer_pid):
                drawer_pid = players[(i + 1) % len(players)]["pid"]
                break
    else:
        drawer_pid = players[0]["pid"]

    await broadcast({
        "header": "new_game",
        "drawer_pid": drawer_pid,
        "start_time": last_game_start.isoformat(),
        "new_sentence": sentences_list[-1]
    })


async def handle_draw(data):
    """
    Handles the draw event from a player.

    This function is called when a player sends a draw event. It appends the received frames to the global frames list
    and broadcasts the received frames to all players except the drawer.

    Parameters:
    data (dict): The data sent by the player, containing drawing information to update the canvas.
    """

    global all_frames

    all_frames += data["frames"]

    await broadcast(data, skip_id=drawer_pid)


async def handle_roll_back(data):
    """
    Handles the roll_back event from a player.

    This function is called when a player requests to rollback the drawing to a previous step.
    It updates the roll_back variable and broadcasts the received roll_back value to all players
    except the drawer.

    Parameters:
    data (dict): The data sent by the player, containing the number of steps to rollback.
    ws (aiohttp.web.WebSocketResponse): The WebSocket connection of the player that sent the event.
    """
    global roll_back

    roll_back = data["roll_back"]

    await broadcast(data, skip_id=drawer_pid)


async def handle_guess(message):
    """
    Handles the guess event from a player.

    This function is called when a player sends a guess event. It checks if the guess is correct
    and if the player is the first one to guess the sentence. If it is, it gives points to the
    player and the drawer. It also broadcasts the guess to all players except the drawer.

    Parameters:
    message (dict): The data sent by the player, containing the guess message and the remaining time.

    """
    global players, drawer_pid, guess_list, sentences_list

    list_found = []
    succeed = False

    message["succeed"] = False

    for i, player in enumerate(players):
        if message["pid"] == player["pid"] and player["pid"] != drawer_pid:
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
                    if players[j]["pid"] == drawer_pid:
                        players[j]["points"] += drawer_points
                        break

                message["new_points"] = [{"pid": player["pid"], "points": founder_points}, {
                    "pid": drawer_pid, "points": drawer_points}]

        if player["pid"] != drawer_pid:
            list_found.append(player["found"])

    guess_list.append(message)

    await broadcast(message)

    # Vérifier si tous les joueurs ont trouvé
    if len(players) > 1 and all(list_found):
        await handle_new_game()


async def handle_emote(message):
    """
    Handle an emote message.

    This function is a callback that is called by aiohttp when an emote message is
    received from a player. It copies the emote asset from the shop directory to the
    temporary assets directory if it does not already exist, and then broadcasts the
    message to all other players.

    Parameters:
    message (dict): The message containing the emote path
    """
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
    """
    Broadcast a message to all connected players.

    This function sends the given message to all connected players, unless they have
    the given skip_id. If a target_pid is given, the message is only sent to the player
    with that ID.

    Parameters:
    message (dict): The message to be sent
    skip_id (int): The ID of the player that should not receive the message
    target_pid (int): The ID of the player that should receive the message. If None,
        the message is sent to all players except the one with skip_id.
    """
    for player in players:
        if player["pid"] != skip_id and (
                target_pid is None or player["pid"] == target_pid):
            await player["ws"].send_json(message)


def get_num_players(request):
    """
    Returns the number of players currently connected.

    This function handles a request to retrieve the number of players
    currently connected to the server. It responds with a JSON object
    containing the count of players.

    Parameters:
    request (aiohttp.web.Request): The request object (not used).

    Returns:
    aiohttp.web.Response: A JSON response with the number of players.
    """

    return web.json_response({"num_players": len(players)})


async def redirect_to_index(request):
    """Redirige vers index.html"""
    raise web.HTTPFound("/index.html")


async def start_web():
    """
    Starts the web server.

    This function sets up the aiohttp web application and begins
    listening for incoming connections on the specified port.

    Parameters:
    None

    Returns:
    None
    """
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
    """
    Retourne un numéro de port TCP libre sur la machine locale.

    La fonction utilise la fonction bind() de la bibliothèque socket
    pour demander un port TCP aléatoire libre sur la machine locale.
    Le numéro du port est ensuite récupéré avec getsockname() et
    retourné.

    Returns:
    int: Le numéro du port TCP libre.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))  # Bind sur un port aléatoire libre
        return s.getsockname()[1]  # Retourne le numéro du port


def start_server(serv_name):
    """
    Démarre le serveur.

    Cette fonction configure les variables du serveur, lance Ngrok,
    configure le serveur web et le lance. Elle exécute ensuite
    une boucle infinie pour maintenir le serveur en vie.

    Parameters:
    serv_name (str): Le nom du serveur, utilisé pour identifier
        les paramètres du serveur dans le fichier de configuration.

    Returns:
    None
    """
    global ngrok, server_started, server_name, loop, players, drawer_pid, guess_list, sentences_list, last_game_start, all_frames, roll_back, port

    # Variables du jeu
    players = []
    drawer_pid = -1
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
    port = get_free_port()
    ngrok.connect(port, domain=CONFIG["servers"][server_name]["domain"])

    loop.run_until_complete(start_web())  # Exécuter le serveur
    server_started = True
    loop.run_forever()


def stop_server():
    """
    Arrête le serveur.

    Cette fonction ferme toutes les WebSockets, stoppe l'application web,
    ferme la connexion Ngrok et arrête la boucle d'événements.

    Returns:
    None
    """
    global app, websockets, server_started, server_name, loop, ngrok

    if not server_started or not loop:
        return

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
        tasks = [t for t in asyncio.all_tasks(
            loop) if t is not asyncio.current_task()]
        [t.cancel() for t in tasks]  # Annuler les tâches actives

        loop.stop()
    asyncio.run_coroutine_threadsafe(shutdown(), loop)


# Fonction pour être compatible avec un import et un lancement direct
if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        stop_server(server_name)
