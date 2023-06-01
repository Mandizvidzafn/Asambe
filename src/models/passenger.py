from .base_model import BaseModel
from .location import Location
from src import db
from flask_login import UserMixin
from sqlalchemy import Sequence


class Passenger(db.Model, BaseModel, UserMixin):
    id = db.Column(
        db.Integer(),
        primary_key=True,
        nullable=False,
        autoincrement=True,
        server_default=db.text("100"),
    )
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean(), default=False)
    lat = db.Column(db.Float(), nullable=True)
    long = db.Column(db.Float(), nullable=True)
    locationId = db.Column(db.Integer(), db.ForeignKey("location.id"))
    newsletter = db.Column(db.Boolean(), default=False)
    number_visibility = db.Column(db.Boolean(), default=False)
    profile_visibility = db.Column(db.Boolean(), default=False)
    role = db.Column(db.String(20), default="passenger", nullable=False)
