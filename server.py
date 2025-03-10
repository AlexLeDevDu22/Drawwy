import json
import os
import yaml
import sys
import threading
import time
from datetime import datetime
import sentences
import tools
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, send
from pyngrok import ngrok

# Charger config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Charger le token ngrok depuis .env
load_dotenv()
ngrok_token = os.getenv("NGROK_AUTH_TOKEN")
ngrok_domain = os.getenv("NGROK_DOMAIN")

# Configuration de ngrok
ngrok.set_auth_token(ngrok_token)

# Initialisation de Flask et SocketIO
app = Flask(__name__, static_folder='./web', static_url_path='/')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading", logger=False, engineio_logger=False, allow_unsafe_werkzeug=True)

# Variables du jeu
players = []
drawer_id = 0
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

@socketio.on('connect')
def handle_connect():
    print("Nouveau client connecté")

@socketio.on('disconnect')
def handle_disconnect():
    global players
    # Trouver le joueur qui s'est déconnecté
    for i, player in enumerate(players):
        if player.get("sid") == request.sid:
            print(f"Joueur {player['pseudo']} déconnecté")
            players.pop(i)
            break

    if player["avatar"]["type"] == "matrix":
        os.remove(f"web/players-avatars/{player["id"]}.bmp")
    
    # Envoyer la mise à jour des joueurs
    emit('player_disconnected', { 
        "id": player["id"]
    }, broadcast=True)
    

@socketio.on('join')
def handle_join(data):
    global players, last_game_start
    
    disconnected_player = 0 if players == [] else players[-1]["id"] + 1
    
    # Envoyer l'ID du joueur et l'état initial du jeu
    emit('welcome', {
        "id": disconnected_player,
        "players": [{"id": p["id"], "pseudo": p["pseudo"], "avatar": p["avatar"], "points": p["points"], "found": p["found"]} for p in players],
        "all_frames": all_frames,
        "messages": guess_list,
        "new_game": last_game_start.isoformat() if last_game_start else False,
        "roll_back": roll_back
    })
    
    # Ajouter le joueur à la liste
    players.append({
        "id": disconnected_player,
        "pseudo": data["pseudo"],
        "avatar": data["avatar"],
        "points": 0,
        "found": False,
        "sid": request.sid
    })

    # enregistrer l'avatar
    if data["avatar"]["type"] == "matrix":
        tools.save_canvas(data["avatar"]["matrix"], "web/players-avatars/"+str(disconnected_player)+".bmp", sentences_list[-1])
    
    # Annoncer le nouveau joueur
    emit('new_player', {
            "id": disconnected_player, 
            "pseudo": data["pseudo"],
            "avatar": data["avatar"],
            "points": 0, 
            "found": False
    }, broadcast=True)
    
    # Démarrer un nouveau jeu si c'est le deuxième joueur
    if len(players) == 2:
        last_game_start = datetime.now()
        emit('update', {
            "frames": None,
            "drawer_id": drawer_id,
            "new_message": None,
            "sentence": sentences_list[-1],
            "found": False,
            "new_game": last_game_start.isoformat(),
            "roll_back": roll_back,
        "new_founder": None,
        "new_points": None
        }, broadcast=True)

@socketio.on('draw')
def handle_draw(data):
    global all_frames
    
    # Mise à jour du dessin
    all_frames += data["frames"]
    
    # Envoyer la mise à jour
    emit('update', {
        "frames": data["frames"],
        "drawer_id": drawer_id,
        "new_message": None,
        "sentence": sentences_list[-1],
        "found": False,
        "new_game": False,
        "roll_back": roll_back,
        "new_founder": None,
        "new_points": None,
        "new_founder": None,
        "new_points": None
    }, broadcast=True)

@socketio.on('roll_back')
def handle_roll_back(data):
    global roll_back
    
    roll_back = data["roll_back"]
    
    emit('update', {
        "frames": None,
        "drawer_id": drawer_id,
        "new_message": None,
        "sentence": sentences_list[-1],
        "found": False,
        "new_game": False,
        "roll_back": roll_back,
        "new_founder": None,
        "new_points": None
    }, broadcast=True)

@socketio.on('guess')
def handle_guess(data):
    global players, drawer_id, guess_list, sentences_list, last_game_start
    
    list_found = []
    succeed = False
    mess = None
    
    for i, player in enumerate(players):
        if player["id"] == data["disconnected_player"]:
            if player["id"] == drawer_id:
                mess = {"guess": data["guess"], "disconnected_player": player["id"], "pseudo": player["pseudo"], "succeed": False}
            else:
                succeed = tools.check_sentences(sentences_list[-1], data["guess"])
                new_points = 0
                if succeed:
                    if not player["found"]:
                        new_points = int((data["remaining_time"] / config["game_duration"]) * len(players) * config["points_per_found"])
                        players[i]["points"] += new_points
                    players[i]["found"] = True
                    
                    # Donner des points au dessinateur
                    for j in range(len(players)):
                        if players[j]["id"] == drawer_id:
                            players[j]["points"] += config["points_per_found"]
                            break
                
                mess = {"guess": data["guess"], "disconnected_player": player["id"], "pseudo": player["pseudo"], "points": new_points, "succeed": succeed}
        
        if player["id"] != drawer_id:
            list_found.append(player["found"])
    
    guess_list.append(mess)
    
    # Vérifier si tous les joueurs ont trouvé
    new_game = False
    if len(players) > 1 and all(list_found):
        new_game = True
        last_game_start = datetime.now()
        
        sentences_list.append(sentences.new_sentence())
        
        for i in range(len(players)):
            players[i]["found"] = False
        
        # Changer de dessinateur
        for i in range(len(players)):
            if int(players[i]["id"]) == int(drawer_id):
                drawer_id = players[(i + 1) % len(players)]["id"]
                break
        
        guess_list = []
    
    emit('update', {
        "frames": None,
        "drawer_id": drawer_id,
        "new_message": mess,
        "sentence": sentences_list[-1],
        "found": False,
        "new_game": last_game_start.isoformat() if new_game else False,
        "roll_back": roll_back,
        "new_founder": data["disconnected_player"] if succeed else None,
        "new_points": [{"disconnected_player": data["disconnected_player"], "points": new_points}, {"disconnected_player": drawer_id, "points": config["points_per_found"]}]
    }, broadcast=True)

@socketio.on('game_finished')
def handle_game_finished():
    global players, drawer_id, guess_list, sentences_list, last_game_start
    
    # Réinitialiser les joueurs
    for i in range(len(players)):
        players[i]["found"] = False
    
    # Changer de dessinateur
    for i in range(len(players)):
        if int(players[i]["id"]) == int(drawer_id):
            drawer_id = players[(i + 1) % len(players)]["id"]
            break
    
    # Nouvelle phrase
    sentences_list.append(sentences.new_sentence())
    
    # Réinitialiser les suppositions
    guess_list = []
    
    # Nouvelle heure de début
    last_game_start = datetime.now()
    
    emit('update', {
        "frames": None,
        "drawer_id": drawer_id,
        "new_message": None,
        "sentence": sentences_list[-1],
        "found": False,
        "new_game": last_game_start.isoformat(),
        "roll_back": roll_back,
        "new_founder": None,
        "new_points": None
    }, broadcast=True)

def flask_worker():
    """Fonction pour exécuter le serveur Flask dans un thread"""
    socketio.run(app, host='0.0.0.0', port=8765, debug=False, use_reloader=False)

def start_server():
    """Démarre le serveur Flask-SocketIO et Ngrok."""
    global server_running, http_tunnel, flask_thread, stop_event
    
    # Réinitialiser l'événement d'arrêt
    stop_event.clear()
    
    # Exposer le port avec ngrok
    http_tunnel = ngrok.connect(8765, "http", domain=ngrok_domain, bind_tls=True)
    
    print(f"Serveur accessible via: {http_tunnel.public_url}")
    print("ok2")
    
    # Démarrer Flask dans un thread séparé
    flask_thread = threading.Thread(target=flask_worker)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Marquer le serveur comme en cours d'exécution
    server_running = True
    
    # Attendre que le serveur soit arrêté
    while not stop_event.is_set() and flask_thread.is_alive():
        time.sleep(0.5)
def stop_server():
    """Arrête proprement le serveur Flask-SocketIO et Ngrok."""
    global server_running, http_tunnel, stop_event
    
    print("Arrêt du serveur en cours...")
    
    # Signaler l'arrêt
    stop_event.set()
    
    # Déconnecter ngrok
    if http_tunnel:
        print("Fermeture du tunnel ngrok...")
        ngrok.disconnect(http_tunnel.public_url)
    
    # Signaler aux clients la fermeture du serveur
    try:
        emit('server_shutdown', {'message': 'Le serveur va s\'arrêter.'}, broadcast=True)
    except Exception as e:
        print(f"Erreur lors de l'envoi du message de fermeture: {e}")

    for filename in os.listdir("web/players-avatars"):
        os.remove(os.path.join("web/players-avatars", filename))
    
    # Marquer le serveur comme arrêté
    server_running = False
    
    print("Serveur arrêté avec succès.")

# Fonction pour être compatible avec un import et un lancement direct
if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        stop_server()