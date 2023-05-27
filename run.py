from src import create_app, socketIO

app = create_app()

if __name__ == "__main__":
    socketIO.run(app, debug=True)
