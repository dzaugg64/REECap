# test_ws.py
from flask import Flask
from flask_sock import Sock

app = Flask(__name__)
sock = Sock(app)


@app.route("/")
def hello():
    return "Hello World!"

@sock.route("/ws")
def websocket_test(ws):
    print("WebSocket route hit!")  # Log when this route is triggered
    while True:
        data = ws.receive()
        if data is None:
            break
        ws.send(f"Echo: {data}")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5010, debug=True, use_reloader=False)
