from flask_restx import Api
from .driver.views import driver_views_ns
from flask import Flask
from src import db
import os
from dotenv import load_dotenv
load_dotenv()

api = Api(doc="/api", title="asambe API", version="2")
db_Name = "asambe"
username = os.getenv("MysqlUSER")
password = os.getenv("PASSWORD")


def create_api_app():
    api_app = Flask("ASAMBE_API")
    api.init_app(api_app)
    api.add_namespace(driver_views_ns)

    api_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"mysql://{username}:{password}@localhost/{db_Name}"
    api_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    api_app.config["SECRET_KEY"] = "hehehehehe"
    db.init_app(api_app)

    return api_app




