"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for, session
from src.forms.passenger import SignupForm, SigninForm, UpdateForm
from src.models.driver import Driver
from src import db, socketio
from flask_socketio import emit
from flask_login import current_user, login_required
from ..multiple_login_required import login_required_with_manager
from ...models.engine import storage


passenger_views = Blueprint("passenger_views", __name__, url_prefix="/passenger")


@passenger_views.route("/")
@passenger_views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if current_user.role == "driver":
        return redirect(url_for("driver_views.home"))
    return render_template("passenger/index.html", user=current_user)


@passenger_views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateForm()
    if request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone
    return render_template("passenger/profile.html", user=current_user, form=form)


@passenger_views.route("/drivers", methods=["GET", "POST"])
@login_required
def drivers():
    if current_user.role == "driver":
        return redirect(url_for("driver_views.passengers"))
    drivers = storage.get_all_filtered_item("driver", "active", True)

    return render_template("passenger/drivers.html", drivers=drivers)


@passenger_views.route("/my-locations", methods=["GET", "POST"])
@login_required
def my_locations():
    if current_user.role == "driver":
        return redirect(url_for("driver_views.my_locations"))
    user = storage.get_item("passenger", current_user.id)

    return render_template("passenger/locations.html", user=user)


# SET locations
@socketio.on("set-default-location")
def set_default_location(data):
    user = storage.get_item("passenger", current_user.id)
    default = data["dlocation"]
    if user and default != None:
        user.location = default
        storage.save()


@socketio.on("set-to-location")
def set_to_location(data):
    user = storage.get_item("passenger", current_user.id)
    to = data["tlocation"]
    if user and to != None:
        user.to = to
        storage.save()


@socketio.on("set-from-location")
def set_from_location(data):
    user = storage.get_item("passenger", current_user.id)
    from_ = data["flocation"]
    if user and from_ != None:
        user.from_loc = from_
        storage.save()


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
