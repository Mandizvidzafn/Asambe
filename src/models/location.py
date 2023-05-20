from .base_model import BaseModel
from .driver import Driver
from .vehicle import Vehicle
from src import db


class Location(db.Model, BaseModel):
    name = db.Column(db.String(40), nullable=False)
    postalcode = db.Column(db.String(40), nullable=False)
    town = db.Column(db.String(45), nullable=False)
    driverId = db.Column(db.Integer(), db.ForeignKey("driver.id"))
    vehicleId = db.Column(db.Integer(), db.ForeignKey("vehicle.id"))
