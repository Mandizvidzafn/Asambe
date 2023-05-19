from sqlalchemy import Column, String, Boolean, Integer
from .base_layout import BaseModel
from .location import Location
from .vehicle import Vehicle
from src import db


class Driver(BaseModel, db.Model):
    firstname = Column(String(40), nullable=False)
    lastname = Column(String(40), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    password = Column(String(45), nullable=False)
    active = Column(Boolean(), default=False)
    locationId = Column(Integer(), db.ForeignKey("location.id"))
    vehicleId = Column(Integer(), db.ForeignKey("vehicle.id"))
