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
    vehicleId = db.Column(db.Integer(), db.ForeignKey("vehicle.id"))
