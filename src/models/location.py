from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from .base_layout import BaseModel
from .driver import Driver
from .vehicle import Vehicle
from src import db


class Location(BaseModel, db.Model):
    name = Column(String(40), nullable=False)
    postalcode = Column(String(40), nullable=False)
    town = Column(String(45), nullable=False)
    driverId = Column(Integer(), ForeignKey("driver.id"))
    vehicleId = Column(Integer(), ForeignKey("vehicle.id"))
