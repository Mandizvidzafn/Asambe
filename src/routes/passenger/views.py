"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.passenger import SignupForm, SigninForm, UpdateForm
from src.models.driver import Driver
from src import db, socketio
from flask_socketio import emit
from flask_login import current_user
from ..multiple_login_required import login_required_with_manager
from src import passenger_login_manager
from ...models.engine import storage


passenger_views = Blueprint("passenger_views", __name__, url_prefix="/passenger")


@passenger_views.route("/")
@passenger_views.route("/home", methods=["GET", "POST"])
@login_required_with_manager(passenger_login_manager)
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("passenger_auth.signin"))
    return render_template("passenger/index.html", user=current_user)


@passenger_views.route("/profile", methods=["GET", "POST"])
@login_required_with_manager(passenger_login_manager)
def profile():
    form = UpdateForm()
    if request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone
    return render_template("passenger/profile.html", user=current_user, form=form)


# show active drivers on passenger map
@socketio.on("active_drivers_location")
def send_drivers_location():
    drivers = storage.get_all_filtered_item("driver", "active", True)

    print("Sending drivers' locations")
    if drivers is not None:
        for driver in drivers:
            driver_id = driver.id
            latitude = driver.lat
            longitude = driver.long
            active = driver.active
            name = f"{driver.firstname} {driver.lastname}"

            data = {
                "active": active,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "driver_id": driver_id,
            }

            emit("driver_location_update", data, broadcast=True)
