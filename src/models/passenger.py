from .base_model import BaseModel
from src import db
from flask_login import UserMixin
from sqlalchemy import Sequence


class Passenger(db.Model, BaseModel, UserMixin):
    id = db.Column(
        db.Integer(),
        Sequence("passnger_id", start=100),
        primary_key=True,
        nullable=False,
    )
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Boolean(), default=False)
    profile_pic = db.Column(db.String(255), nullable=True, default="default.jpg")
    lat = db.Column(db.Float(), nullable=True)
    long = db.Column(db.Float(), nullable=True)
    to = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    from_loc = db.Column(db.String(120), nullable=True)
    newsletter = db.Column(db.Boolean(), default=False)
    number_visibility = db.Column(db.Boolean(), default=False)
    profile_visibility = db.Column(db.Boolean(), default=False)
    role = db.Column(db.String(20), default="passenger", nullable=False)
