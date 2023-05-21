"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.driver import SignupForm, SigninForm
from src.models.driver import Driver
from src import db
from flask_login import login_required, current_user


driver_views = Blueprint("driver_views", __name__, url_prefix="/driver")


@driver_views.route("/")
@driver_views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    return render_template("driver/home.html", user=current_user)
