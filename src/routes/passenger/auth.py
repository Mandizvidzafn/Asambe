from flask import (
    Blueprint,
    redirect,
    render_template,
    flash,
    url_for,
    session,
)
from flask_login import login_user, logout_user, current_user, login_required
from ..multiple_login_required import login_required_with_manager
from src.forms.passenger import (
    SigninForm,
    SignupForm,
    ForgotPasswordForm,
    VerifyOTPForm,
)
from src.models.passenger import Passenger
from src import db, socketio
from flask_socketio import emit
from ..get_location_name import location_name
from flask_bcrypt import check_password_hash, generate_password_hash
from twilio.rest import Client
from dotenv import load_dotenv
import os
from ...models.engine import storage
from ..generate_ids import generate_passenger_id

passenger_auth = Blueprint("passenger_auth", __name__, url_prefix="/passenger")


load_dotenv()

from_phone = os.getenv("TWILIO_PHONE_NUMBER")
auth_token = os.getenv("ACCOUNT_AUTH_TOKEN")
account_sid = os.getenv("ACCOUNT_SID")
verify_sid = os.getenv("VERIFY_SID")
reset_sid = os.getenv("RESET_SID")
client = Client(account_sid, auth_token)


@passenger_auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        newsletter = form.newsletter.data
        password = form.password.data

        hashed_password = generate_password_hash(password, rounds=12)

        user = storage.get_filtered_item("driver", "phone", phone)
        if user:
            form.phone.errors.append("Phone number exists")
        else:
            new_user = Passenger(
                id=generate_passenger_id(),
                lastname=lastname,
                firstname=firstname,
                phone=phone,
                newsletter=newsletter,
                password=hashed_password,
            )

            storage.create(new_user)
            storage.save()
            session["phone"] = phone
            send_otp = client.verify.services(verify_sid).verifications.create(
                to=phone, channel="sms"
            )
            if send_otp.sid:
                return redirect(url_for("passenger_auth.verify_otp"))
    return render_template("passenger/signup.html", form=form)


""" @passenger_auth.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("driver_views.home"))

    form = SigninForm()

    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data

        existing_passenger = storage.get_filtered_item("passenger", "phone", phone)
        if existing_passenger:
            print(existing_passenger.phone)
            if check_password_hash(existing_passenger.password, password):
                login_user(existing_passenger)
                return redirect(url_for("passenger_views.home"))
            else:
                flash("incorrect phone or password")
        else:
            flash("passenger doesn't exist")
    return render_template("passenger/signin.html", form=form) """


@passenger_auth.route("/retrieve-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        phone = form.phone.data

        session["phone"] = phone
        send_otp = client.verify.services(reset_sid).verifications.create(
            to=phone, channel="sms"
        )
        if send_otp.sid:
            return redirect(url_for("passenger_auth.verify_otp"))

    return render_template("passenger/forgot_password.html", form=form)


@passenger_auth.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    form = VerifyOTPForm()

    if form.validate_on_submit():
        otp = form.otp.data

        try:
            otp_int = int(otp)
        except ValueError:
            flash("OTP should contain only numbers", "error")
            return render_template("passenger/verify_otp.html", form=form)
        if len(str(otp_int)) != 6:
            flash("OTP should be a 6-digit code", "error")
        else:
            phone = session.get("phone")
            verify_otp_code = client.verify.services(
                verify_sid
            ).verification_checks.create(to=phone, code=otp_int)
            if verify_otp_code.status == "approved":
                session.clear()
                existing_passenger = storage.get_filtered_item(
                    "passenger", "phone", phone
                )
                login_user(existing_passenger)
                return redirect(url_for("passenger_views.home"))
            else:
                flash("Wrong OTP")
    return render_template("passenger/verify_otp.html", form=form)


@passenger_auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("passenger_auth.signin"))


# live location
@socketio.on("passenger_location_update")
def handle_location_update(data):
    passenger_id = current_user.id
    latitude = data["latitude"]
    longitude = data["longitude"]

    # Update the driver's location in the database
    passenger = storage.get_item("passenger", passenger_id)
    if passenger:
        passenger.lat = latitude
        passenger.long = longitude
        db.session.commit()

    passengers = storage.get_all_filtered_item("passenger", "status", True)
    if passengers is not None:
        for passenger in passengers:
            if passenger.status == True:
                passenger_id = passenger.id
                latitude = passenger.lat
                longitude = passenger.long
                name = f"{passenger.firstname} {passenger.lastname}"
                location = location_name(latitude, longitude)

                data = {
                    "passenger_id": passenger_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": name,
                    "location": location,
                }
                emit("passenger_location_update", data, broadcast=True)

            # Emit the location update to all connected clients
            emit("location_update", data, broadcast=True)


# upadte the active status
@socketio.on("passenger_status_update")
def handle_status_update(data):
    passenger_id = current_user.id
    status = data["status"]

    passenger = storage.get_item("passenger", passenger_id)
    if passenger:
        print("updating passenger status")
        passenger.status = status
        print(passenger.status)
        db.session.commit()

        if not status:
            emit(
                "remove_inactive_passengers",
                {"passenger_ids": [passenger_id]},
                broadcast=True,
            )

    emit("status_update", {"status": status}, broadcast=True)
