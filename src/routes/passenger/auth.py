"""auth.py"""
from flask import redirect, render_template, request, Blueprint, url_for, flash, session
from src.forms.passenger import (
    SignupForm,
    SigninForm,
    ForgotPasswordForm,
    VerifyOTPForm,
)
from src.models.passenger import Passenger
from src import db
from flask_login import login_user, logout_user
from flask_bcrypt import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import os
from twilio.rest import Client
from ..multiple_login_required import login_required_with_manager
from src import passenger_login_manager

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
    print("before validate")
    print(form.firstname.data)
    print(form.lastname.data)
    print(form.phone.data)
    print(form.password.data)
    print(form.confirm_password.data)
    print(form.newsletter.data)
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        password = form.password.data
        newsletter = form.newsletter.data
        hashed_password = generate_password_hash(password, rounds=12)
        check_phone = Passenger.query.filter_by(phone=phone).first()
        if check_phone:
            form.phone.errors.append("Phone number exits. Sign in instead")
        else:
            new_user = Passenger(
                firstname=firstname,
                lastname=lastname,
                phone=phone,
                password=hashed_password,
                newsletter=newsletter,
            )
            db.session.add(new_user)
            db.session.commit()
            session["phone"] = phone
            send_otp = client.verify.services(verify_sid).verifications.create(
                to=phone, channel="sms"
            )
            if send_otp.sid:
                return redirect(url_for("passenger_auth.verify_otp"))

    return render_template("passenger/signup.html", form=form)


@passenger_auth.route("/signin", methods=["GET", "POST"])
def signin():
    form = SigninForm()
    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data

        existing_user = Passenger.query.filter_by(phone=phone).first()
        if existing_user:
            if check_password_hash(existing_user.password, password):
                login_user(existing_user, remember=True)
                return redirect(url_for("passenger_views.home"))
            else:
                flash("Phone number or Password is incorrect", "error")
        else:
            flash("Account doesn't exist", "error")
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
            phone = session.clear("phone")
            verify_otp_code = client.verify.services(
                verify_sid
            ).verification_checks.create(to=phone, code=otp_int)
            if verify_otp_code.status == "approved":
                return redirect(url_for("passenger_views.home"))
            else:
                flash("Wrong OTP", "error")
    return render_template("passenger/verify_otp.html", form=form)


@passenger_auth.route("/logout", methods=["GET", "POST"])
@login_required_with_manager(passenger_login_manager)
def logout():
    session.clear()
    login_user()
    return redirect(url_for("passenger_auth.signin"))
