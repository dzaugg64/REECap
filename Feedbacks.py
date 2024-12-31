import json

# Stockage des connexions WebSocket
clients = {}

def emit_feedback(client_id, message, subtitle = ""):
    """Send feedback to a specific client."""
    if client_id in clients:
        try:
            msg = json.dumps({"type": "status", "message": message, "subtitle": subtitle})
            clients[client_id].send(msg)
        except Exception as e:
            print(f"Error sending feedback to {client_id}: {e}")

def update_progressbar(client_id, percentage):
    """Update prograssBart of  a specific client."""
    if client_id in clients:
        try:
            msg = json.dumps({"type": "progress", "percentage": percentage})
            clients[client_id].send(msg)
        except Exception as e:
            print(f"Error sending feedback to {client_id}: {e}")