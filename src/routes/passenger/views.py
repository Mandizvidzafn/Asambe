"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.passenger import SignupForm, SigninForm
from src.models.passenger import Passenger
from src import db
from flask_login import current_user
from ..multiple_login_required import login_required_with_manager
from src import passenger_login_manager


passenger_views = Blueprint("passenger_views", __name__, url_prefix="/passenger")


@passenger_views.route("/")
@passenger_views.route("/home", methods=["GET", "POST"])
@login_required_with_manager(passenger_login_manager)
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("passenger_auth.signin"))
    return render_template("passenger/home.html", user=current_user)
