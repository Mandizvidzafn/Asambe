"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.passenger import SignupForm, SigninForm
from src.models.driver import Driver
from src import db, socketio
from flask_socketio import emit
from flask_login import current_user, user_logged_in
from ..multiple_login_required import login_required_with_manager
from src import passenger_login_manager


passenger_views = Blueprint("passenger_views", __name__, url_prefix="/passenger")


@passenger_views.route("/")
@passenger_views.route("/home", methods=["GET", "POST"])
@login_required_with_manager(passenger_login_manager)
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("passenger_auth.signin"))
    return render_template("passenger/index.html", user=current_user)


# show active drivers on map
@socketio.on("active_drivers_location")
def send_drivers_location():
    drivers = Driver.query.filter_by(active=True).all()
    print("Sending drivers' locations")
    for driver in drivers:
        driver_id = driver.id
        latitude = driver.lat
        longitude = driver.long
        name = f"{driver.firstname} {driver.lastname}"

        data = {
            "driver_id": driver_id,
            "latitude": latitude,
            "longitude": longitude,
            "name": name,
        }

        emit("driver_location_update", data, broadcast=True)
