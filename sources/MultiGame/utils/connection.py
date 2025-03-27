import asyncio
from asyncio import exceptions
import websockets
import threading
import MultiGame.utils.tools as tools
from shared.utils.data_manager import *
import time
from datetime import datetime
import pygame

def start_connexion(MultiGameClass, server_name):
    """
    Initializes and starts a connection for the multiplayer game.

    This function attempts to test the server specified by `server_name`. If the server is not
    running, it starts the server in a separate thread and waits for it to initialize. Once the
    server is running, it sets up an asyncio event loop and handles the client connection.

    Args:
        MultiGameClass: The instance of the multiplayer game class.
        server_name (str): The name of the server to connect to.

    Raises:
        asyncio.exceptions.CancelledError: If the connection setup is cancelled.
    """
    try:
        if not tools.test_server(server_name):  # start the serv

            import MultiGame.server as server
            MultiGameClass.server = server
            threading.Thread(
                target=server.start_server, args=(
                    server_name,), daemon=True).start()

            while not server.server_started:
                time.sleep(0.1)

        asyncio.set_event_loop(MultiGameClass.connection_loop)
        MultiGameClass.connection_loop.run_until_complete(
            handle_connection_client(MultiGameClass, server_name, is_server=bool(MultiGameClass.server), port=server.port if MultiGameClass.server else None))
    except asyncio.exceptions.CancelledError:
        print("connexion fermé")


async def handle_connection_client(MultiGame, server_name, is_server, port=None):
    """
    Handles the client connection to the server.

    This function is run in its own asyncio event loop and handles all communication with the server.

    It sets up event listeners for the following events:

        - welcome: sets up the game state and initializes the canvas
        - new_player: adds a new player to the game state
        - player_disconnected: removes a player from the game state
        - new_game: resets the game state and starts a new game
        - draw: updates the canvas in real time
        - new_message: adds a new message to the chat
        - roll_back: rolls back the canvas to a previous state

    Parameters:
        MultiGame: the instance of the MultiGame class
        server_name: the name of the server to connect to
        is_server: a boolean indicating whether the server is running locally or not
        port: the port number to use if the server is running locally
    """
    def welcome(data):
        """
        Handles the welcome event from the server.

        The welcome event is sent when the client connects to the server and
        initializes the game state.

        Parameters:
            data (dict): the data sent by the server
        """
        MultiGame.connected = True
        MultiGame.ALL_FRAMES += data["all_frames"]
        MultiGame.PLAYER_ID = data["pid"]
        MultiGame.MESSAGES = data["messages"]
        MultiGame.PLAYERS = data["players"]
        MultiGame.CURRENT_SENTENCE = data["sentence"]
        MultiGame.CURRENT_DRAWER = data["drawer_pid"]
        tools.update_canva_by_frames(
            MultiGame, data["all_frames"], delay=False)

    def new_player(data):
        """
        Handles the new_player event from the server.

        The new_player event is sent when a new player joins the game and
        adds the new player to the game state.

        Parameters:
            data (dict): the data sent by the server
        """
        MultiGame.PLAYERS.append(data)
        MultiGame.MESSAGES.append({"type": "system",
                                   "message": data["pseudo"] + " viens de nous rejoindre!",
                                   "color": CONFIG["succeed_color"]})

    def player_disconnected(data):
        """
        Handles the player_disconnected event from the server.

        The player_disconnected event is sent when a player leaves the game and
        removes the player from the game state.

        Parameters:
            data (dict): the data sent by the server
        """
        
        
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
        """
        Handles the new_game event from the server.

        The new_game event is sent when a new game starts and resets the game state.

        Parameters:
            data (dict): the data sent by the server
        """
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
        MultiGame.CURRENT_DRAWER = data["drawer_pid"]
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
        """
        Handles the draw event from the server.

        This function is responsible for updating the canvas in real-time for all
        players except the current drawer. It processes the incoming frames and
        updates the drawing state accordingly.

        Parameters:
            frames (dict): The frames data sent by the server, containing drawing
            information to update the canvas.

        Side Effects:
            - Updates the `MultiGame.ALL_FRAMES` with new drawing frames.
            - Resets `MultiGame.ROLL_BACK` to 0.
            - Starts a new thread to update the canvas with the provided frames.
            - Calculates and updates the number of drawing steps in
            `MultiGame.STEP_NUM`.
        """
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
        """
        Handles the new_message event from the server.

        The new_message event is sent when a new message is sent by a player and
        adds the new message to the game state.

        If the message is a guess and the player is the current player, it checks
        if it is the first message of the current player and gives an achievement
        if it is.

        Parameters:
            mess (dict): the data sent by the server
        """
        if mess["pid"] == MultiGame.PLAYER_ID:
            num_my_mess = 0
            for i in range(len(MultiGame.MESSAGES)-1, -1, -1):
                if MultiGame.MESSAGES[i]["type"] != "system" and MultiGame.MESSAGES[i]["pid"] == mess["pid"]:
                    num_my_mess+=1
                    if num_my_mess == 1:
                        MultiGame.MESSAGES.pop(i)
            
            if num_my_mess == 1 and mess["type"] == "guess" and mess["succeed"]: # succeed and first message
                MultiGame.achievements_manager.new_achievement(3)

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
        """
        Handles the roll_back event from the server.

        The roll_back event is sent when another player requests to rollback to a previous step
        in the drawing. If the current player is not the current drawer, it updates the `MultiGame.ROLL_BACK`
        and resets the canvas to the previous step.

        Parameters:
            roll_back (int): the step number to rollback to
        """
        if MultiGame.PLAYER_ID != MultiGame.CURRENT_DRAWER:
            MultiGame.ROLL_BACK = roll_back
            tools.update_canva_by_frames(
                MultiGame, MultiGame.ALL_FRAMES, reset=True, delay=False)

    async with websockets.connect(f"ws://localhost:{port}/ws" if is_server else f"wss://{CONFIG["servers"][server_name]["domain"]}/ws") as websocket:
        MultiGame.WS = websocket

        MultiGame.is_connected = True

        await websocket.send(json.dumps({"header": "join",
                                          "pseudo": PLAYER_DATA["pseudo"],
                                            "avatar": {"type": "matrix", 
                                                       "matrix": tools.load_bmp_to_matrix("data/avatar.bmp"),
                                                        "border_path": SHOP_ITEMS[PLAYER_DATA["selected_items"]["Bordures"]]["image_path"] if PLAYER_DATA["selected_items"]["Bordures"] else None,
                                                        "has_border": bool(PLAYER_DATA["selected_items"]["Bordures"])}
                                        })
                            )

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



async def shutdown(loop, MultiGame):
    """
    Arrête proprement la boucle asyncio et ferme la WebSocket si elle est ouverte.

    Cette fonction est appelée lorsque le serveur est fermé.
    """
    try:
        print("Début de la fermeture...")

        # Fermer la WebSocket proprement si elle est ouverte
        if MultiGame.WS and not MultiGame.WS.closed:
            try:
                await asyncio.wait_for(MultiGame.WS.close(), timeout=3)
                print("WebSocket fermée proprement")
            except asyncio.TimeoutError:
                print("⚠️ Timeout lors de la fermeture de la WebSocket")

        # Annuler toutes les tâches asyncio en attente
        tasks = [t for t in asyncio.all_tasks(loop) if not t.done()]
        print(f"{len(tasks)} tâches en cours d'annulation...")

        for task in tasks:
            task.cancel()
            try:
                await asyncio.wait_for(task, timeout=2)  # On force l'attente max 2s
            except asyncio.CancelledError:
                pass
            except asyncio.TimeoutError:
                print("⚠️ Une tâche a mis trop de temps à s'annuler")

        # Fermer proprement la boucle asyncio
        print("Arrêt de la boucle asyncio...")
        loop.stop()

    except Exception as e:
        print(f"Erreur lors de l'arrêt : {e}")

    finally:
        print("Fermeture terminée ✅")

def disconnect(MultiGame):
    """
    Arrête la connexion du client au serveur et ferme la WebSocket.

    Cette fonction est appelée lorsque le bouton "Déconnexion" est cliqué.

    - Ferme la WebSocket si elle est ouverte
    - Annule toutes les tâches asyncio en attente
    - Ferme la boucle asyncio
    - Stoppe le serveur si il est lancé
    - Met à jour l'état de la connexion
    - Attend la fin du thread de connexion
    """
    if MultiGame.connection_loop and not MultiGame.connection_loop.is_closed():
        future = asyncio.run_coroutine_threadsafe(shutdown(MultiGame.connection_loop, MultiGame), MultiGame.connection_loop)
        future.result(timeout=5)  # On attend max 5s pour éviter un blocage

    if MultiGame.server:
        MultiGame.server.stop_server()
        MultiGame.server = None

    MultiGame.is_connected = False

    # Attendre la fin du thread de connexion
    if MultiGame.connexion_thread:
        MultiGame.connexion_thread.join()