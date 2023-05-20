from .base_model import BaseModel
from .location import Location
from src import db
from flask_login import UserMixin


class Passenger(db.Model, BaseModel, UserMixin):
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.Boolean(), default=False)
    locationId = db.Column(db.Integer(), db.ForeignKey("location.id"))
    newsletter = db.Column(db.Boolean(), default=False)
