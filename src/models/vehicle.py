from sqlalchemy import Column, String
from .base_layout import BaseModel
from src import db


class Vehicle(BaseModel, db.Model):
    type = Column(String(20), unique=True)
