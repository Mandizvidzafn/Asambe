from .base_model import BaseModel
from .vehicle import Vehicle
from src import db
from flask_login import UserMixin
from sqlalchemy import Sequence


class Driver(db.Model, BaseModel, UserMixin):
    id = db.Column(
        db.Integer(), Sequence("driver_id", start=101), primary_key=True, nullable=False
    )
    firstname = db.Column(db.String(40), nullable=False)
    lastname = db.Column(db.String(40), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean(), default=False)
    lat = db.Column(db.Float(), nullable=True)
    long = db.Column(db.Float(), nullable=True)
    end_loc = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    start_loc = db.Column(db.String(120), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True, default="default.jpg")
    vehicle_type = db.Column(db.String(50), db.ForeignKey("vehicle.type"))
    vehicle = db.relationship("Vehicle", backref="drivers")
    newsletter = db.Column(db.Boolean(), default=False)
    role = db.Column(db.String(20), default="driver", nullable=False)
