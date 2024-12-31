from flask import Flask
from flask_sock import Sock
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/ws": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "allow_headers": ["*"]
    }
})

sock = Sock(app)

# Configuration spécifique pour Flask-Sock
'''
app.config['SOCK_SERVER_OPTIONS'] = {
    'ping_interval': 25,
    'ping_timeout': 10,
    'close_timeout': 10
}'''

@app.route("/")
def hello():
    return "Hello World!"

@sock.route("/ws")
def websocket_test(ws):
    print("WebSocket route hit!")  # Log when this route is triggered
    try:
        while True:
            data = ws.receive()
            if data is None:
                break
            print(f"Received: {data}")  # Log received data
            ws.send(f"Echo: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        print("WebSocket connection closed")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)