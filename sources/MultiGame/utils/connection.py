import asyncio
import websockets
import threading
import MultiGame.utils.tools as tools
from shared.utils.data_manager import *
import time
from datetime import datetime
import pygame

connection_loop = None

def start_connexion(MultiGameClass, server_name):
    try:
        if not tools.test_server(server_name):  # start the serv

            import MultiGame.server as server
            MultiGameClass.server = server
            threading.Thread(
                target=server.start_server, args=(
                    server_name,), daemon=True).start()

            while not server.server_started:
                time.sleep(0.1)

        global connection_loop
        connection_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(connection_loop)
        MultiGameClass.connection_loop.run_until_complete(
            handle_connection_client(MultiGameClass, server_name, is_server=bool(MultiGameClass.server), port=server.port if MultiGameClass.server else None))
    except RuntimeError:
        print("connexion fermé")


async def handle_connection_client(MultiGame, server_name, is_server, port=None):

    def welcome(data):
        MultiGame.connected = True
        MultiGame.ALL_FRAMES += data["all_frames"]
        MultiGame.PLAYER_ID = data["pid"]
        MultiGame.MESSAGES = data["messages"]
        MultiGame.PLAYERS = data["players"]
        MultiGame.CURRENT_SENTENCE = data["sentence"]
        MultiGame.CURRENT_DRAWER = data["drawer_id"]
        tools.update_canva_by_frames(
            MultiGame, data["all_frames"], delay=False)

    def new_player(data):
        MultiGame.PLAYERS.append(data)
        MultiGame.MESSAGES.append({"type": "system",
                                   "message": data["pseudo"] + " viens de nous rejoindre!",
                                   "color": CONFIG["succeed_color"]})

    def player_disconnected(data):
        for i in range(len(MultiGame.PLAYERS)):
            if MultiGame.PLAYERS[i]["pid"] == data["pid"]:
                player = MultiGame.PLAYERS.pop(i)
                MultiGame.MESSAGES.append(
                    {
                        "type": "system",
                        "message": player["pseudo"] +
                        " à quitté la partie.",
                        "color": CONFIG["bad_color"]})
                break

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

    def draw(frames):
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:  # not the drawer
            MultiGame.ALL_FRAMES = tools.split_steps_by_roll_back(
                MultiGame.ALL_FRAMES, MultiGame.ROLL_BACK)[0]
            MultiGame.ROLL_BACK = 0

            threading.Thread(
                target=tools.update_canva_by_frames,
                kwargs={
                    "MultiGame": MultiGame,
                    "frames": frames["frames"]}).start()  # update canvas in realtime

            num_steps = 0
            for frame in MultiGame.ALL_FRAMES:
                if frame["type"] == "new_step":
                    num_steps += 1
            MultiGame.STEP_NUM = num_steps

    def new_message(mess):
        # ajouter à la liste de message
        if mess["pid"] == MultiGame.PLAYER_ID:
            for i in range(len(MultiGame.MESSAGES)-1, -1, -1):
                if MultiGame.MESSAGES[i]["type"] != "system" and MultiGame.MESSAGES[i]["pid"] == mess["pid"]:
                    MultiGame.MESSAGES.pop(i)
                    break
        MultiGame.MESSAGES.append(mess)

        # update found and points
        if mess["type"] == "guess":
            if mess["succeed"]:
                for i in range(len(MultiGame.PLAYERS)):
                    if MultiGame.PLAYERS[i]["pid"] == mess["pid"]:
                        MultiGame.PLAYERS[i]["found"] = True

                for e in mess["new_points"]:
                    for i in range(len(MultiGame.PLAYERS)):
                        if MultiGame.PLAYERS[i]["pid"] == e["pid"]:
                            MultiGame.PLAYERS[i]["points"] += e["points"]
                            if e["pid"] == MultiGame.PLAYER_ID:
                                PLAYER_DATA["coins"] += e["points"]
                                save_data("PLAYER_DATA")

    def roll_back(roll_back):
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:
            MultiGame.ROLL_BACK = roll_back
            tools.update_canva_by_frames(
                MultiGame, MultiGame.ALL_FRAMES, reset=True, delay=False)

    async with websockets.connect(f"ws://localhost:{port}/ws" if is_server else f"wss://{CONFIG["servers"][server_name]["domain"]}/ws") as websocket:
        MultiGame.WS = websocket

        MultiGame.is_connected = True

        await websocket.send(json.dumps({"header": "join", "pseudo": PLAYER_DATA["pseudo"], "avatar": {"type": "matrix", "matrix": tools.load_bmp_to_matrix("data/avatar.bmp"), "border_path": SHOP_ITEMS[PLAYER_DATA["selected_items"]["Bordures"]]["image_path"]}}))

        async for message in websocket:
            data = json.loads(message)

            if data["header"] == "welcome":
                welcome(data)
            elif data["header"] == "new_player":
                new_player(data)
            elif data["header"] == "player_disconnected":
                player_disconnected(data)
            elif data["header"] == "new_game":
                new_game(data)
            elif data["header"] == "draw":
                draw(data)
            elif data["header"] == "new_message":
                new_message(data)
            elif data["header"] == "roll_back":
                roll_back(data)
            elif data["header"] == "draw":
                draw(data)


def disconnect(MultiGame):
    global connection_loop
    if MultiGame.connection_loop.is_running():
        def cancel_tasks(loop):
            asyncio.set_event_loop(loop)
            for task in asyncio.all_tasks(loop):
                task.cancel()
            loop.stop()

        MultiGame.connection_loop.call_soon_threadsafe(
            cancel_tasks, MultiGame.connection_loop)

    if MultiGame.server:
        MultiGame.server.stop_server()
        MultiGame.server = None
    MultiGame.is_connected = False
    # Attendre la fin du thread de connexion
    #MultiGame.connexion_thread.join()
    print("Déconnexion terminée.")
