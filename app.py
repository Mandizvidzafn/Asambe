import eventlet
from src import create_app, socketio

eventlet.monkey_patch(socket=False)

app = create_app()

if __name__ == "__main__":
    socketio.run(app, debug=True, host="0.0.0.0")
