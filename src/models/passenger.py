from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from .base_layout import BaseModel
from .location import Location
from src import db


class Passenger(BaseModel, db.Model):
    firstname = Column(String(40), nullable=False)
    lastname = Column(String(40), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    password = Column(String(45), nullable=False)
    status = Column(Boolean(), default=False)
    locationId = Column(Integer(), ForeignKey("location.id"))
