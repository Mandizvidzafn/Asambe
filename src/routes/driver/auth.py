from flask import Blueprint, redirect, render_template, flash, url_for, session
from flask_login import login_user, logout_user, current_user
from ..multiple_login_required import login_required_with_manager
from src import driver_login_manager
from src.forms.driver import SigninForm, SignupForm, ForgotPasswordForm, VerifyOTPForm
from src.models.driver import Driver
from src.models.vehicle import Vehicle
from src import db, socketio
from flask_socketio import emit
from flask_bcrypt import check_password_hash, generate_password_hash
from twilio.rest import Client
from dotenv import load_dotenv
import os
from ..get_location_name import location_name
from ...models.engine import storage

driver_auth = Blueprint("driver_auth", __name__, url_prefix="/driver")


load_dotenv()

from_phone = os.getenv("TWILIO_PHONE_NUMBER")
auth_token = os.getenv("ACCOUNT_AUTH_TOKEN")
account_sid = os.getenv("ACCOUNT_SID")
verify_sid = os.getenv("VERIFY_SID")
reset_sid = os.getenv("RESET_SID")
client = Client(account_sid, auth_token)


@driver_auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        vehicle_type = form.vehicle.data
        newsletter = form.newsletter.data
        password = form.password.data

        vehicle_id = storage.get_item("vehicle", vehicle_type)

        hashed_password = generate_password_hash(password, rounds=12)

        user = storage.get_filtered_item("driver", "phone", phone)
        if user:
            form.phone.errors.append("Phone number exists")
        else:
            new_user = Driver(
                lastname=lastname,
                firstname=firstname,
                phone=phone,
                vehicle=vehicle_id,
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
                return redirect(url_for("driver_auth.verify_otp"))
    return render_template("driver/signup.html", form=form)


@driver_auth.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("driver_views.home"))

    form = SigninForm()

    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data

        existing_driver = storage.get_filtered_item("driver", "phone", phone)
        if existing_driver:
            if check_password_hash(existing_driver.password, password):
                session["phone"] = phone
                login_user(existing_driver, remember=True)
                return redirect(url_for("driver_views.home"))
            else:
                flash("incorrect phone or password")
        else:
            flash("driver doesn't exist")
    return render_template("driver/signin.html", form=form)


@driver_auth.route("/retrieve-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("driver_views.home"))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        phone = form.phone.data

        session["phone"] = phone
        send_otp = client.verify.services(reset_sid).verifications.create(
            to=phone, channel="sms"
        )
        if send_otp.sid:
            return redirect(url_for("driver_auth.verify_otp"))

    return render_template("driver/forgot_password.html", form=form)


@driver_auth.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    if current_user.is_authenticated:
        return redirect(url_for("driver_views.home"))

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
                existing_driver = storage.get_filtered_item("driver", "phone", phone)
                login_user(existing_driver, remember=True)
                return redirect(url_for("driver_views.home"))
            else:
                flash("Wrong OTP")
    return render_template("driver/verify_otp.html", form=form)


@driver_auth.route("/logout", methods=["GET", "POST"])
@login_required_with_manager(driver_login_manager)
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("driver_auth.signin"))


# live location
@socketio.on("location_update")
def handle_location_update(data):
    driver_id = current_user.id
    latitude = data["latitude"]
    longitude = data["longitude"]

    # Update the driver's location in the database
    driver = storage.get_item("driver", driver_id)
    if driver:
        driver.lat = latitude
        driver.long = longitude
        db.session.commit()

    drivers = storage.get_all_filtered_item("driver", "active", True)
    if drivers is not None:
        for driver in drivers:
            if driver.active == True:
                driver_id = driver.id
                latitude = driver.lat
                longitude = driver.long
                name = f"{driver.firstname} {driver.lastname}"
                location = location_name(latitude, longitude)

                data = {
                    "driver_id": driver_id,
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": name,
                    "location": location,
                }
                emit("driver_location_update", data, broadcast=True)

            # Emit the location update to all connected clients
            emit("location_update", data, broadcast=True)


# upadte the active status
@socketio.on("status_update")
def handle_status_update(data):
    driver_id = current_user.id
    status = data["status"]

    driver = storage.get_item("driver", driver_id)
    if driver:
        print("updating driver status")
        driver.active = status
        db.session.commit()

        if not status:
            emit("remove_inactive_drivers", {"driver_ids": [driver_id]}, broadcast=True)

    emit("status_update", {"status": status}, broadcast=True)
