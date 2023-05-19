from flask_sqlalchemy import SQLAlchemy
from flask import Flask


db_Name = "asambe.db"
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_Name}"
    app.config["SECRET_KEY"] = "hehehehehe"

    db.init_app(app)

    return app
