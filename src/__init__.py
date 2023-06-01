from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from os import path
from flask_login import LoginManager
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

login_manager = LoginManager()

db_Name = "asambe"
db = SQLAlchemy()
socketio = SocketIO()
username = os.getenv("MysqlUSER")
password = os.getenv("PASSWORD")


def create_app():
    app = Flask(__name__)

    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql://{username}:{password}@localhost/{db_Name}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = "hehehehehe"

    # initializations
    db.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.signin"

    # Models
    from .models.passenger import Passenger
    from .models.driver import Driver
    from .models.location import Location
    from .models.vehicle import Vehicle

    @login_manager.user_loader
    def load_user(user_id):
        passenger_user = Passenger.query.get(user_id)
        driver_user = Driver.query.get(user_id)

        if driver_user:
            return Driver.query.get(int(user_id))
        elif passenger_user:
            return Passenger.query.get(int(user_id))

    # create the database
    create_database(app)

    # Registering blueprints
    from .routes.passenger.auth import passenger_auth
    from .routes.passenger.views import passenger_views
    from .routes.driver.auth import driver_auth
    from .routes.driver.views import driver_views
    from .routes.admin.view import admin_views
    from .routes.admin.auth import admin_auth
    from .routes.authentication import auth

    app.register_blueprint(passenger_auth)
    app.register_blueprint(passenger_views)
    app.register_blueprint(driver_auth)
    app.register_blueprint(driver_views)
    app.register_blueprint(admin_views)
    app.register_blueprint(admin_auth)
    app.register_blueprint(auth)

    return app


def create_database(app):
    import mysql.connector

    mydb = mysql.connector.connect(host="localhost", user=username, password=password)
    my_cursor = mydb.cursor()
    my_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_Name}")
    my_cursor.close()
    mydb.database = db_Name

    with app.app_context():
        # create the tables
        db.create_all()

        # Reset auto-increment values
        db.session.execute(
            text("ALTER TABLE driver AUTO_INCREMENT = 100, AUTO_INCREMENT = 2")
        )
        db.session.execute(
            text("ALTER TABLE passenger AUTO_INCREMENT = 101, AUTO_INCREMENT = 2")
        )
        db.session.commit()
