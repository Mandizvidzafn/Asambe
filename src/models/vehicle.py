from .base_model import BaseModel
from src import db


class Vehicle(db.Model, BaseModel):
    type = db.Column(db.String(20), unique=True)
