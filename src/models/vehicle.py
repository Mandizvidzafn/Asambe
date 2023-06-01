from .base_model import BaseModel
from src import db


class Vehicle(db.Model, BaseModel):
    id = db.Column(db.Integer(), primary_key=True, nullable=False)
    type = db.Column(db.String(20), unique=True)
