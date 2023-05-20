from flask import Blueprint, redirect, render_template, flash, url_for
from flask_login import login_required
from src.forms.driver import SigninForm, SignupForm, ForgotPasswordForm, VerifyOTPForm
from src.models.driver import Driver
from src import db
from flask_bcrypt import check_password_hash, generate_password_hash

driver_auth = Blueprint("driver_auth", __name__, url_prefix="/driver")


@driver_auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        vehicle = form.vehicle.data
        newsletter = form.newsletter.data
        password = form.password.data

        hashed_password = generate_password_hash(password, rounds=12, salt_size=16)

        user = Driver.query.filter_by(phone=phone).first()
        if user:
            form.phone.errors.append("Phone number exists")
        else:
            new_user = Driver(
                lastname=lastname,
                firstname=firstname,
                phone=phone,
                vehicle=vehicle,
                newsletter=newsletter,
                password=hashed_password,
            )

            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("driver_auth.verify_otp"))
    return render_template("driver/signup.html", form=form)


@driver_auth.route("/signin", methods=["GET", "POST"])
def signin():
    form = SigninForm()

    if form.validate_on_submit():
        phone = form.phone.data
        password = form.password.data

        existing_driver = Driver.query.filter_by(phone=phone)
        if existing_driver:
            if check_password_hash(existing_driver.password, password):
                return redirect(url_for("driver_views.home"))
            else:
                flash("incorrect phone or password")
        else:
            flash("driver doesn't exist")
    return render_template("driver/signin.html", form=form)


@driver_auth.route("/retrieve-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        phone = form.phone.data

        return redirect(url_for("driver_auth.verify_otp"))

    return render_template("driver/forgot_password.html", form=form)


@driver_auth.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    form = VerifyOTPForm()

    if form.validate_on_submit():
        if form.validate_on_submit():
            otp = form.otp.data

            if not int(otp):
                flash("OTP is a 6 digit code")
            else:
                return redirect(url_for("driver_views.home"))

    return render_template("driver/verify_otp.html", form=form)
