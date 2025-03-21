from shared.utils.data_manager import *

import requests
import os
import threading
import time
from datetime import datetime
import MultiGame.utils.sentences as sentences
import MultiGame.utils.tools as tools
from flask import Flask, request
from flask_socketio import SocketIO, emit
import shutil
from pyngrok import ngrok

# Initialisation de Flask et SocketIO
app = Flask(__name__, static_folder='web', static_url_path='/')
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading",
    logger=False,
    engineio_logger=False,
    allow_unsafe_werkzeug=True)

server_name = None

# Variables du jeu
players = []
drawer_id = -1
guess_list = []
sentences_list = [sentences.new_sentence()]
last_game_start = None
all_frames = []
roll_back = 0

# Variables pour le serveur
server_running = False
http_tunnel = None
flask_thread = None
stop_event = threading.Event()

# Route principale pour servir l'index.html


@app.route('/')
def index():
    return app.send_static_file('index.html')


@app.route('/num_players', methods=['GET'])
def get_player_count():
    return {"num_players": len(players)}, 200


@socketio.on('connect')
def handle_connect():
    print("Nouveau client connecté")


@socketio.on('disconnect')
def handle_disconnect(data=None):
    global players
    if players:
        # Trouver le joueur qui s'est déconnecté
        for i, player in enumerate(players):
            if player.get("sid") == request.sid:
                print(f"Joueur {player['pseudo']} déconnecté")
                players.pop(i)
                break

        if player["avatar"]["type"] == "matrix" and os.path.exists(
                f"sources/MultiGame/web/temp-assets/avatars/{player['pid']}.bmp"):
            os.remove(f"sources/MultiGame/web/temp-assets/avatars/{player["pid"]}.bmp")

        # Envoyer la mise à jour des joueurs
        emit('player_disconnected', {
            "pid": player["pid"],
            "pseudo": player["pseudo"]
        }, broadcast=True)


@socketio.on('join')
def handle_join(data):
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
        "sid": request.sid
    })

    # Envoyer l'ID du joueur et l'état initial du jeu
    emit('welcome',
         {"pid": pid,
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
          "roll_back": roll_back})

    # enregistrer l'avatar
    if data["avatar"]["type"] == "matrix":
        tools.save_canvas(data["avatar"]["matrix"],
                          "sources/MultiGame/web/temp-assets/avatars/" + str(pid) + ".bmp",
                          sentences_list[-1],
                          False)

    # Annoncer le nouveau joueur
    emit('new_player', {
        "pid": pid,
        "pseudo": data["pseudo"],
        "avatar": data["avatar"],
        "points": 0,
        "found": False
    }, broadcast=True, skip_sid=request.sid)

    if len(players) == 2:
        handle_new_game()


@socketio.on('game_finished')
def handle_new_game(data=None):
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

    emit('new_game', {
        "drawer_id": drawer_id,
        "start_time": last_game_start.isoformat(),
        "new_sentence": sentences_list[-1]
    }, broadcast=True)


@socketio.on('draw')
def handle_draw(frames):
    global all_frames

    # Mise à jour du dessin
    all_frames += frames

    # Envoyer la mise à jour
    emit('draw', frames, broadcast=True, skip_sid=request.sid)


@socketio.on('roll_back')
def handle_roll_back(data_roll_back):
    global roll_back

    roll_back = data_roll_back

    emit('roll_back', roll_back, broadcast=True, skip_sid=request.sid)


@socketio.on('message')
def handle_message(message):
    global players, drawer_id, guess_list, sentences_list, last_game_start

    if message["type"] == "guess":
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
                print(player["pid"], player["found"])
                list_found.append(player["found"])

        guess_list.append(message)

        emit('new_message', message, broadcast=True)

        # Vérifier si tous les joueurs ont trouvé
        if len(players) > 1 and all(list_found):
            handle_new_game()

    elif message['type'] == "emote":
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

        emit('new_message', message, broadcast=True)


def flask_worker():
    """Fonction pour exécuter le serveur Flask dans un thread"""
    socketio.run(
        app,
        host='0.0.0.0',
        port=8765,
        debug=False,
        use_reloader=False)


def start_server(serv_name):
    """Démarre le serveur Flask-SocketIO et Ngrok."""
    global server_running, http_tunnel, flask_thread, stop_event, server_name

    server_name = serv_name

    # Réinitialiser l'événement d'arrêt
    stop_event.clear()

    # Configuration de ngrok
    from pyngrok import ngrok
    ngrok.set_auth_token(CONFIG["servers"][server_name]["auth_token"])
    ngrok.set_api_key(CONFIG["servers"][server_name]["api"])

    # Exposer le port avec ngrok
    http_tunnel = ngrok.connect(
        8765,
        "http",
        domain=CONFIG["servers"][server_name]["domain"],
        bind_tls=True)

    print(f"Serveur accessible via: {http_tunnel.public_url}")

    try:
        # Démarrer Flask dans un thread séparé
        flask_thread = threading.Thread(target=flask_worker)
        flask_thread.daemon = True
        flask_thread.start()

        # Marquer le serveur comme en cours d'exécution
        server_running = True

        # Attendre que le serveur soit arrêté
        while not stop_event.is_set() and flask_thread.is_alive():
            time.sleep(0.5)

    except KeyboardInterrupt:
        stop_server()


def stop_server():
    """Arrête proprement le serveur Flask-SocketIO et Ngrok."""
    global server_running, http_tunnel, stop_event, server_name

    if not server_name:
        return

    print("Arrêt du serveur en cours...")

    # Signaler l'arrêt
    stop_event.set()

    # Déconnecter ngrok
    if http_tunnel:
        print("Fermeture du tunnel ngrok...")
        ngrok.disconnect(http_tunnel.public_url)

    # Signaler aux clients la fermeture du serveur
    # try:
    #     emit('server_shutdown', {'message': 'Le serveur va s\'arrêter.'}, broadcast=True)
    # except Exception as e:
    #     print(f"Erreur lors de l'envoi du message de fermeture: {e}")

    for filename in os.listdir("sources/MultiGame/web/temp-assets/avatars"):
        os.remove(os.path.join("sources/MultiGame/web/temp-assets/avatars", filename))

    # Au cas ou...
    try:
        endpoints = requests.get(
            "https://api.ngrok.com/endpoints",
            headers={
                "Authorization": "Bearer " +
                CONFIG["servers"][server_name]["api"],
                "Ngrok-Version": "2"}).json()["endpoints"]
        if endpoints:
            requests.delete(
                "https://api.ngrok.com/endpoints/" +
                endpoints[0]["id"],
                headers={
                    "Authorization": "Bearer " +
                    CONFIG["servers"][server_name]["api"],
                    "Ngrok-Version": "2"})

        ts = requests.get(
            "https://api.ngrok.com/tunnel_sessions",
            headers={
                "Authorization": "Bearer " +
                "2uBh0vcHjqPdwVi3t4gz9D9ZEH9_3R1frHq58vY8VQEzSuUMW",
                "Content-Type": "application/json",
                "Ngrok-Version": "2"},
            json={}).json()["tunnel_sessions"]

        if ts:
            requests.post(
                "https://api.ngrok.com/tunnel_sessions/" +
                ts[0]["id"] +
                "/stop",
                headers={
                    "Authorization": "Bearer " +
                    "2uBh0vcHjqPdwVi3t4gz9D9ZEH9_3R1frHq58vY8VQEzSuUMW",
                    "Content-Type": "application/json",
                    "Ngrok-Version": "2"},
                json={}).json()
    except BaseException:
        pass

    ngrok.kill()

    from pyngrok import ngrok as ngrok2
    ngrok2.get_tunnels()
    ngrok2.kill()

    # Marquer le serveur comme arrêté
    server_running = False

    print("Serveur arrêté avec succès.")


# Fonction pour être compatible avec un import et un lancement direct
if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        stop_server(server_name)
