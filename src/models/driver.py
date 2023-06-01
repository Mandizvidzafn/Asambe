from .base_model import BaseModel
from .vehicle import Vehicle
from src import db
from flask_login import UserMixin
from sqlalchemy import Sequence


class Driver(db.Model, BaseModel, UserMixin):
    id = db.Column(
        db.Integer(),
        primary_key=True,
        nullable=False,
        autoincrement=True,
        server_default=db.text("101"),
    )
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=False)
    lat = db.Column(db.Float(), nullable=True)
    long = db.Column(db.Float(), nullable=True)
    vehicle_type = db.Column(db.String(50), db.ForeignKey("vehicle.type"))
    vehicle = db.relationship("Vehicle", backref="drivers")
    newsletter = db.Column(db.Boolean(), default=False)
    role = db.Column(db.String(20), default="driver", nullable=False)
