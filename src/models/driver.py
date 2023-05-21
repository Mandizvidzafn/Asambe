from .base_model import BaseModel
from .vehicle import Vehicle
from src import db
from flask_login import UserMixin


class Driver(db.Model, BaseModel, UserMixin):
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(45), nullable=False)
    active = db.Column(db.Boolean(), default=False)
    vehicle_type = db.Column(db.String(), db.ForeignKey("vehicle.type"))
    vehicle = db.relationship("Vehicle", backref="drivers")
    newsletter = db.Column(db.Boolean(), default=False)
