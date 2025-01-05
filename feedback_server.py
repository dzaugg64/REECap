import sys
if "pydevd" in sys.modules:
    DEBUG = True
    import logging
    logging.basicConfig(level=logging.DEBUG)
else:
    DEBUG = False

import json
import uuid
from flask import Flask
from flask_cors import CORS
from flask_sock import Sock
import redis

# Initialisation de Flask et Flask-Sock
app = Flask(__name__)
CORS(app)  # Activer les CORS pour toutes les routes
sock = Sock(app)

# Configuration de Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Stockage des connexions WebSocket
clients = {}

@sock.route('/feedback')
def feedback(ws):
    """
    Gère les connexions WebSocket, envoie un client_id au client et diffuse les messages Redis.
    """
    # Génère un client_id unique et stocke la connexion WebSocket
    client_id = str(uuid.uuid4())
    clients[client_id] = ws

    # Envoie le client_id au client dès l'ouverture de la connexion
    ws.send(json.dumps({"type": "client_id", "client_id": client_id}))

    # Configure le pubsub Redis pour écouter les messages sur feedback_channel
    pubsub = redis_client.pubsub()
    pubsub.subscribe("feedback_channel")

    try:
        # Diffuse les messages Redis au client concerné
        for message in pubsub.listen():
            if message["type"] == "message":
                feedback_data = json.loads(message["data"].decode("utf-8"))
                client_ws = clients.get(feedback_data["client_id"])
                if client_ws:
                    client_ws.send(json.dumps(feedback_data))
    except Exception as e:
        print(f"Erreur WebSocket : {e}")
    finally:
        # Supprime le client du dictionnaire lors de la déconnexion
        del clients[client_id]

def emit_feedback(redis_client, client_id, message, subtitle=""):
    """
    Publie un message de feedback dans Redis.
    """
    feedback_message = {
        "client_id": client_id,
        "type": "status",
        "message": message,
        "subtitle": subtitle
    }
    redis_client.publish("feedback_channel", json.dumps(feedback_message))

def update_progressbar(redis_client, client_id, percentage):
    """
    Publie une mise à jour de la barre de progression dans Redis.
    """
    progress_message = {
        "client_id": client_id,
        "type": "progress",
        "percentage": percentage
    }
    redis_client.publish("feedback_channel", json.dumps(progress_message))

def close_websocket(redis_client, client_id):
    """
    Envoie une commande pour fermer le WebSocket d'un client.
    """
    close_message = {
        "client_id": client_id,
        "type": "close"
    }
    redis_client.publish("feedback_channel", json.dumps(close_message))

def hide_overlay(redis_client, client_id):
    """
    Envoie une commande pour désactiver l'overlay de téléchargement.
    """
    overlay_message = {
        "client_id": client_id,
        "type": "file_uploaded"
    }
    redis_client.publish("feedback_channel", json.dumps(overlay_message))



if __name__ == "__main__":
    if DEBUG:
        gunicorn_logger = logging.getLogger('gunicorn.error')
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    print("Lancement du serveur Flask...")
    app.run(host='127.0.0.1', port=6000, debug=DEBUG, use_reloader=False)