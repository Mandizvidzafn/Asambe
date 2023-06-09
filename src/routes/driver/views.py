"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.driver import SignupForm, SigninForm, UpdateForm
from src.models.driver import Driver
from src import db, socketio
from flask_socketio import emit
from ...models.engine import storage
from flask_login import current_user, user_logged_in, login_required


driver_views = Blueprint("driver_views", __name__, url_prefix="/driver")


@driver_views.route("/")
@driver_views.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if current_user.role == "passenger":
        return redirect(url_for("passenger_views.home"))
    print(f"current user id is {current_user.id}")
    return render_template("driver/index.html", user=current_user)


@driver_views.route("/passengers", methods=["GET", "POST"])
@login_required
def passengers():
    if current_user.role == "passenger":
        return redirect(url_for("passenger_views.drivers"))
    passengers = storage.get_all_filtered_item("passenger", "status", True)

    return render_template("driver/passengers.html", passengers=passengers)


@driver_views.route("/my-locations", methods=["GET", "POST"])
@login_required
def my_locations():
    if current_user.role == "passenger":
        return redirect(url_for("passenger_views.my_locations"))
    user = storage.get_item("driver", current_user.id)

    return render_template("driver/locations.html", user=user)


# SET locations
@socketio.on("set-default-location")
def set_default_location(data):
    user = storage.get_item("driver", current_user.id)
    default = data["dlocation"]
    if user and default != None:
        user.location = default
        storage.save()


@socketio.on("set-start-location")
def set_to_location(data):
    user = storage.get_item("driver", current_user.id)
    start = data["slocation"]
    print(start)
    if user and start != None:
        user.start_loc = start
        storage.save()


@socketio.on("set-end-location")
def set_from_location(data):
    user = storage.get_item("driver", current_user.id)
    end = data["elocation"]
    print(end)
    if user and end != None:
        user.end_loc = end
        storage.save()


# show active passengers on driver map
@socketio.on("active_passengers_location")
def send_passengers_location():
    passengers = storage.get_all_filtered_item("passenger", "status", True)

    print("Sending passengers' locations")
    if passengers is not None:
        for passenger in passengers:
            passenger_id = passenger.id
            latitude = passenger.lat
            longitude = passenger.long
            active = passenger.status
            name = f"{passenger.firstname} {passenger.lastname}"
            print(f"passenger name: {passenger.firstname}")

            data = {
                "active": active,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "passenger_id": passenger_id,
            }

            emit("passenger_location_update", data, broadcast=True)
