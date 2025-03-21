import asyncio
import socketio
import threading
import MultiGame.utils.tools as tools
from shared.utils.data_manager import *
import os
from dotenv import load_dotenv
import time
from datetime import datetime
import pygame

connection_loop = None


def start_connexion(MultiGameClass, server_name):
    try:

        if not asyncio.run(tools.test_server(server_name)):  # start the serv

            import MultiGame.server as server
            MultiGameClass.server = server
            threading.Thread(
                target=server.start_server, args=(
                    server_name,), daemon=True).start()

            while not server.server_running:
                time.sleep(0.1)

        global connection_loop
        connection_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(connection_loop)
        MultiGameClass.connection_loop.run_until_complete(
            handle_connection_client(MultiGameClass, server_name))
    except RuntimeError:
        print("connexion fermé")


async def handle_connection_client(MultiGame, server_name):

    MultiGame.SIO = socketio.AsyncClient(logger=True, engineio_logger=True)

    @MultiGame.SIO.event
    async def connect():  # joining the game

        await MultiGame.SIO.emit("join", {"type": "join", "pseudo": PLAYER_DATA["pseudo"], "avatar": {"type": "matrix", "matrix": tools.load_bmp_to_matrix("data/avatar.bmp"), "border_path": SHOP_ITEMS[PLAYER_DATA["selected_items"]["Bordures"]]["image_path"]}})

    @MultiGame.SIO.event
    async def disconnect():
        print("Déconnecté du serveur WebSocket.")

    @MultiGame.SIO.on('welcome')
    async def welcome(data):
        MultiGame.connected = True
        MultiGame.ALL_FRAMES += data["all_frames"]
        MultiGame.PLAYER_ID = data["pid"]
        MultiGame.MESSAGES = data["messages"]
        MultiGame.PLAYERS = data["players"]
        MultiGame.CURRENT_SENTENCE = data["sentence"]
        MultiGame.CURRENT_DRAWER = data["drawer_id"]
        tools.update_canva_by_frames(
            MultiGame, data["all_frames"], delay=False)

    @MultiGame.SIO.on("new_player")
    async def new_player(data):
        MultiGame.PLAYERS.append(data)
        MultiGame.MESSAGES.append({"type": "system",
                                   "message": data["pseudo"] + " viens de nous rejoindre!",
                                   "color": CONFIG["succeed_color"]})

    @MultiGame.SIO.on("player_disconnected")
    async def player_disconnected(data):
        for i in range(len(MultiGame.PLAYERS)):
            print(MultiGame.PLAYERS[i]["pid"], data["pid"])
            if MultiGame.PLAYERS[i]["pid"] == data["pid"]:
                player = MultiGame.PLAYERS.pop(i)
                if MultiGame.PLAYER_ID != player["pid"]:
                    MultiGame.MESSAGES.append(
                        {
                            "type": "system",
                            "message": player["pseudo"] +
                            " à quitté la partie.",
                            "color": CONFIG["bad_color"]})
                break

    @MultiGame.SIO.on("new_game")
    def new_game(data):
        # save draw
        if MultiGame.PLAYER_ID == MultiGame.CURRENT_DRAWER and MultiGame.CANVAS:  # save your draw
            tools.save_canvas(
                MultiGame.CANVAS,
                f"assets/your_best_draws/{
                    datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.bmp",
                MultiGame.CURRENT_SENTENCE,
                True)

        MultiGame.CANVAS = pygame.Surface(
            (MultiGame.canvas_rect.width,
             MultiGame.canvas_rect.height))  # reset canvas
        MultiGame.CANVAS.fill((255, 255, 255))
        MultiGame.CURRENT_SENTENCE = data["new_sentence"]
        MultiGame.CURRENT_DRAWER = data["drawer_id"]
        MultiGame.ALL_FRAMES = []
        for i in range(len(MultiGame.PLAYERS)):
            MultiGame.PLAYERS[i]["found"] = False
            if MultiGame.PLAYERS[i]["pid"] == MultiGame.CURRENT_DRAWER:
                MultiGame.MESSAGES.append(
                    {
                        "type": "system",
                        "message": "Nouvelle partie ! C'est le tour de " +
                        MultiGame.PLAYERS[i]["pseudo"],
                        "color": CONFIG["succeed_color"]})
        MultiGame.GAMESTART = datetime.fromisoformat(data["start_time"])
        MultiGame.ROLL_BACK = 0

    @MultiGame.SIO.on("draw")
    async def draw(frames):
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:  # not the drawer
            MultiGame.ALL_FRAMES = tools.split_steps_by_roll_back(
                MultiGame.ALL_FRAMES, MultiGame.ROLL_BACK)[0]
            MultiGame.ROLL_BACK = 0

            threading.Thread(
                target=tools.update_canva_by_frames,
                kwargs={
                    "MultiGame": MultiGame,
                    "frames": frames}).start()  # update canvas in realtime

            num_steps = 0
            for frame in MultiGame.ALL_FRAMES:
                if frame["type"] == "new_step":
                    num_steps += 1
            MultiGame.STEP_NUM = num_steps

    @MultiGame.SIO.on("new_message")
    def new_message(guess):
        # ajouter à la liste de message
        if guess["pid"] == MultiGame.PLAYER_ID:
            for i in range(len(MultiGame.MESSAGES)):
                if MultiGame.MESSAGES[i]["type"] != "system" and MultiGame.MESSAGES[i]["pid"] == guess["pid"]:
                    MultiGame.MESSAGES.pop(i)
        MultiGame.MESSAGES.append(guess)

        # update found and points
        if guess["type"] == "guess":
            if guess["succeed"]:
                for i in range(len(MultiGame.PLAYERS)):
                    if MultiGame.PLAYERS[i]["pid"] == guess["pid"]:
                        MultiGame.PLAYERS[i]["found"] = True

                for e in guess["new_points"]:
                    for i in range(len(MultiGame.PLAYERS)):
                        if MultiGame.PLAYERS[i]["pid"] == e["pid"]:
                            MultiGame.PLAYERS[i]["points"] += e["points"]
                            if e["pid"] == MultiGame.PLAYER_ID:
                                PLAYER_DATA["coins"] += e["points"]
                                save_data("PLAYER_DATA")

    @MultiGame.SIO.on("roll_back")
    async def roll_back(roll_back):
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:
            MultiGame.ROLL_BACK = roll_back
            tools.update_canva_by_frames(
                MultiGame, MultiGame.ALL_FRAMES, reset=True, delay=False)

    try:
        await MultiGame.SIO.connect(f"https://{CONFIG["servers"][server_name]["domain"]}")

        # enregistrer la partie
        PLAYER_DATA["multi_game_played"] += 1
        save_data("PLAYER_DATA")

        # Boucle pour écouter et réagir aux messages
        await MultiGame.SIO.wait()
    except asyncio.CancelledError:
        print("déconnecté du server")


def disconnect(MultiGame):
    global connection_loop
    if MultiGame.connection_loop.is_running():
        # Arrêter proprement la connexion Socket.IO
        future = asyncio.run_coroutine_threadsafe(
            MultiGame.SIO.disconnect(), MultiGame.connection_loop
        )
        future.result()

        # Annuler toutes les tâches en les récupérant dans le bon thread
        def cancel_tasks(loop):
            asyncio.set_event_loop(loop)
            for task in asyncio.all_tasks(loop):
                task.cancel()
            loop.stop()

        MultiGame.connection_loop.call_soon_threadsafe(
            cancel_tasks, MultiGame.connection_loop)

    # Vérifier et arrêter le serveur si nécessaire
    print(MultiGame.server)
    if MultiGame.server:
        MultiGame.server.stop_server()

    # Attendre la fin du thread de connexion
    MultiGame.connexion_thread.join()
    print("Déconnexion terminée.")
