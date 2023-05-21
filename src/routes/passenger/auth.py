"""auth.py"""
from flask import redirect, render_template, request, Blueprint, url_for, flash
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

passenger_auth = Blueprint("passenger_auth", __name__, url_prefix="/passenger")


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

        return redirect(url_for("passenger_auth.verify_otp"))

    return render_template("passenger/forgot_password.html", form=form)


@passenger_auth.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    form = VerifyOTPForm()

    if form.validate_on_submit():
        if form.validate_on_submit():
            otp = form.otp.data

            if not int(otp):
                flash("OTP is a 6 digit code")
            else:
                return redirect(url_for("passenger_views.home"))

    return render_template("passenger/verify_otp.html", form=form)
