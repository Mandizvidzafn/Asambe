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


@driver_views.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateForm()
    if request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone
    return render_template("driver/profile.html", user=current_user, form=form)


# show active passengers on driver map
@socketio.on("active_passengers_location")
def send_passengers_location():
    passengers = storage.get_all_filtered_item("passengers", "status", True)

    print("Sending passengers' locations")
    if passengers is not None:
        for passenger in passengers:
            passenger_id = passenger.id
            latitude = passenger.lat
            longitude = passenger.long
            active = passenger.active
            name = f"{passenger.firstname} {passenger.lastname}"

            data = {
                "active": active,
                "name": name,
                "latitude": latitude,
                "longitude": longitude,
                "passenger_id": passenger_id,
            }

            emit("passenger_location_update", data, broadcast=True)
