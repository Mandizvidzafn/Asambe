"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.passenger import SignupForm, SigninForm
from src.models.passenger import Passenger
from src import db
from flask_login import login_required


passenger_views = Blueprint("passenger_views", __name__)


@passenger_views.route("/")
@passenger_views.route("/passenger/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("passenger/home.html")
