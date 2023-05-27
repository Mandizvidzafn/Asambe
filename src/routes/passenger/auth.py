from flask import Blueprint, redirect, render_template, flash, url_for, session
from flask_login import login_user, logout_user, current_user
from ..multiple_login_required import login_required_with_manager
from src import passenger_login_manager
from src.forms.passenger import (
    SigninForm,
    SignupForm,
    ForgotPasswordForm,
    VerifyOTPForm,
)
from src.models.passenger import Passenger
from src import db
from flask_bcrypt import check_password_hash, generate_password_hash
from twilio.rest import Client
from dotenv import load_dotenv
import os

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
    if current_user.is_authenticated:
        return redirect(url_for("passenger_views.home"))

    form = SignupForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        newsletter = form.newsletter.data
        password = form.password.data
        hashed_password = generate_password_hash(password, rounds=12)

        user = Passenger.query.filter_by(phone=phone).first()
        if user:
            form.phone.errors.append("Phone number exists")
        else:
            new_user = Passenger(
                lastname=lastname,
                firstname=firstname,
                phone=phone,
                newsletter=newsletter,
                password=hashed_password,
            )

            db.session.add(new_user)
            db.session.commit()
            print(new_user)
            session["phone"] = phone
            print(session.get("phone"))
            send_otp = client.verify.services(verify_sid).verifications.create(
                to=phone, channel="sms"
            )
            if send_otp.sid:
                return redirect(url_for("passenger_auth.verify_otp"))
    return render_template("passenger/signup.html", form=form)


@passenger_auth.route("/signin", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for("passenger_views.home"))

    form = SigninForm()

    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data
        remember_me = form.remember_me.data
        print(remember_me)

        existing_passenger = Passenger.query.filter_by(phone=phone).first()
        if existing_passenger:
            if check_password_hash(existing_passenger.password, password):
                login_user(existing_passenger, remember=True)
                return redirect(url_for("passenger_views.home"))
            else:
                flash("incorrect phone or password")
        else:
            flash("passenger doesn't exist")
    return render_template("passenger/signin.html", form=form)


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
                return redirect(url_for("passenger_views.home"))
            else:
                flash("Wrong OTP")
    return render_template("passenger/verify_otp.html", form=form)


@passenger_auth.route("/logout", methods=["GET", "POST"])
@login_required_with_manager(passenger_login_manager)
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("passenger_auth.signin"))
