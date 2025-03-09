from flask import Flask
from flask_socketio import SocketIO, send
from pyngrok import ngrok

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return "Serveur Flask opérationnel !"

@socketio.on('connect')
def test_connect():
    print("Un client s'est connecté via WebSocket")


@socketio.on('message')
def handle_message(msg):
    print(f"Message reçu : {msg}")
    send(f"Réponse du serveur : {msg}")

if __name__ == '__main__':
    # Démarrer le tunnel ngrok
    public_url = ngrok.connect(8765, "http", domain="vital-mastiff-publicly.ngrok-free.app", bind_tls=True)
    print(f"Tunnel public disponible à : {public_url}")

    # Démarrer le serveur Flask-SocketIO
    socketio.run(app, port=8765)
