from flask import (
    Blueprint,
    redirect,
    render_template,
    flash,
    url_for,
    session,
    request,
    current_app,
)
from flask_login import login_user, logout_user, current_user, login_required
from ..multiple_login_required import login_required_with_manager
from src.forms.passenger import (
    SigninForm,
    SignupForm,
    ForgotPasswordForm,
    VerifyOTPForm,
    UpdateForm,
)
from src.models.passenger import Passenger
from src import db, socketio, photos
from flask_socketio import emit
from ..get_location_name import location_name
from flask_bcrypt import check_password_hash, generate_password_hash
from twilio.rest import Client
from dotenv import load_dotenv
import os
from ...models.engine import storage
from ..generate_ids import generate_passenger_id
from werkzeug.utils import secure_filename
from uuid import uuid4
from PIL import Image

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
        newsletter = form.newsletter.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        phone = form.phone.data
        hashed_password = generate_password_hash(password, rounds=12)

        user = storage.get_filtered_item("passenger", "phone", phone)
        if user:
            form.phone.errors.append("Phone number exists")
            print("phone exists")

        elif password != confirm_password:
            print("not equal")
            form.password.errors.append("passwords must match")
            form.confirm_password.errors.append("passwords must match")
        elif len(password) < 7:
            form.password.errors.append("password must be 7 or more characters")
        else:
            session["phone"] = phone
            session["lastname"] = lastname
            session["firstname"] = firstname
            session["newsletter"] = newsletter
            session["password"] = hashed_password
            send_otp = client.verify.services(verify_sid).verifications.create(
                to=phone, channel="sms"
            )
            if send_otp.sid:
                return redirect(url_for("passenger_auth.signup_verify_otp"))
    return render_template("passenger/signup.html", form=form)


@passenger_auth.route("/signup_verify_otp", methods=["GET", "POST"])
def signup_verify_otp():
    form = VerifyOTPForm()

    if form.validate_on_submit():
        otp = form.otp.data

        try:
            otp_int = int(otp)
        except ValueError:
            form.otp.errors.append(
                "OTP should contain only numbers",
            )
            return render_template("passenger/verify_otp.html", form=form)
        if len(str(otp_int)) != 6:
            print(otp_int)
            print(f"length is {len(str(otp_int))}")
            form.otp.errors.append("OTP must be only 6 digits")
        else:
            print(otp_int)
            print(f"length is {len(str(otp_int))}")
            phone = session.get("phone")
            lastname = session.get("lastname")
            firstname = session.get("firstname")
            newsletter = session.get("newsletter")
            hashed_password = session.get("password")

            verify_otp_code = client.verify.services(
                verify_sid
            ).verification_checks.create(to=phone, code=otp_int)
            if verify_otp_code.status == "approved":
                new_user = Passenger(
                    lastname=lastname,
                    firstname=firstname,
                    phone=phone,
                    newsletter=newsletter,
                    password=hashed_password,
                )
                storage.create(new_user)
                storage.save()
                session.clear()
                login_user(new_user, remember=True)
                return redirect(url_for("passenger_views.home"))
            else:
                flash("Wrong OTP")
    return render_template("passenger/verify_otp.html", form=form)


@passenger_auth.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if current_user.role == "driver":
        return redirect(url_for("driver_auth.profile"))
    form = UpdateForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        confirm_password = form.confirm_password.data
        password = form.password.data
        pic = form.profile_image.data
        user = storage.get_item("passenger", current_user.id)
        if firstname:
            print("changing")
            user.firstname = firstname
        if lastname:
            user.lastname = lastname
        if phone:
            if phone[0] != "+":
                form.phone.errors.append(
                    "phone number should be in international format"
                )
            else:
                if phone != user.phone:
                    check_phone = storage.get_filtered_item("passenger", "phone", phone)
                    if check_phone:
                        form.phone.errors.append(
                            "phone number exists and not changed, choose another"
                        )
                    else:
                        user.phone = phone
        if password != "":
            if len(password) >= 7:
                print("not empty")
                if password != confirm_password:
                    form.confirm_password.errors.append("passwords must match")
                    form.password.errors.append("passwords must match")
                    print(f"form errors {form.password.errors}")
                else:
                    hashed_password = generate_password_hash(password, rounds=12)
                    user.password = hashed_password
            else:
                form.confirm_password.errors.append(
                    "passwords must be greater than 6 characters"
                )
                form.password.errors.append(
                    "passwords must be greater than 6 characters"
                )

        if pic:
            print("there is pic")
            print(type(pic))
            check_pic = secure_filename(pic.filename)
            pic_name = str(uuid4()) + "_" + check_pic

            import imghdr

            if imghdr.what(pic) not in ["jpeg", "jpg", "png"]:
                form.profile_image.errors.append(
                    "Invalid file format. Only JPEG and PNG are allowed"
                )

            else:
                img = Image.open(pic)
                max_size = (250, 250)
                img.thumbnail(max_size)
                # remove the existing pic
                if user.profile_pic != "default.jpg":
                    path_to_old_pic = os.path.join(
                        current_app.config["UPLOADED_PHOTOS_DEST"], user.profile_pic
                    )
                    print(path_to_old_pic)
                    print("Not default")
                    if os.path.exists(path_to_old_pic):
                        os.remove(path_to_old_pic)
                        print("about to change default")
                        # save the the new pic

                        img.save(
                            os.path.join(
                                current_app.config["UPLOADED_PHOTOS_DEST"], pic_name
                            )
                        )
                        user.profile_pic = pic_name
                    else:
                        img.save(
                            os.path.join(
                                current_app.config["UPLOADED_PHOTOS_DEST"], pic_name
                            )
                        )
                        user.profile_pic = pic_name

                else:
                    # just save the the new pic if its equal to defaul.jpg
                    print("changing pic")
                    img.save(
                        os.path.join(
                            current_app.config["UPLOADED_PHOTOS_DEST"], pic_name
                        )
                    )
                    user.profile_pic = pic_name

        storage.save()
    else:
        print("form not valid")

    if request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone

    return render_template("passenger/profile.html", user=current_user, form=form)


@passenger_auth.route("/retrieve-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        phone_intl = form.phone.data
        existing_passenger = storage.get_filtered_item("passenger", "phone", phone_intl)

        if existing_passenger:
            session["phone"] = phone_intl
            send_otp = client.verify.services(reset_sid).verifications.create(
                to=phone_intl, channel="sms"
            )
            if send_otp.sid:
                return redirect(url_for("passenger_auth.verify_otp"))
        else:
            print("doesnt exist")
            form.phone.errors.append("Phone Number is not registred")
            print(f"errprs: {form.phone.errors}")

    return render_template("passenger/forgot_password.html", form=form)


@passenger_auth.route("/verify_otp", methods=["GET", "POST"])
def verify_otp():
    form = VerifyOTPForm()

    if form.validate_on_submit():
        otp = form.otp.data

        try:
            otp_int = int(otp)
        except ValueError:
            form.otp.errors.append("OTP should contain only numbers")
            return render_template("passenger/verify_otp.html", form=form)
        if len(str(otp_int)) != 6:
            form.otp.errors.append("OTP must be only 6 digits")
        else:
            phone = session.get("phone")
            verify_otp_code = client.verify.services(
                reset_sid
            ).verification_checks.create(to=phone, code=otp)
            if verify_otp_code.status == "approved":
                existing_passenger = storage.get_filtered_item(
                    "passenger", "phone", phone
                )
                session.clear()
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
        storage.save()

        if not status:
            emit(
                "remove_inactive_passengers",
                {"passenger_ids": [passenger_id]},
                broadcast=True,
            )

    emit("status_update", {"status": status}, broadcast=True)


# profile visibility
@socketio.on("profile_visibility")
def profile_visibility(data):
    passenger_id = current_user.id
    visibility = data["pro_visibility"]

    passenger = storage.get_item("passenger", passenger_id)
    if passenger:
        print("updating passenger profile_visibility")
        passenger.profile_visibility = visibility
        print(passenger.profile_visibility)
        storage.save()


# number visibility
@socketio.on("number_visibility")
def number_visibility(data):
    passenger_id = current_user.id
    visibility = data["num_visibility"]

    passenger = storage.get_item("passenger", passenger_id)
    if passenger:
        print("updating passenger number_visibility")
        passenger.number_visibility = visibility
        print(passenger.number_visibility)
        storage.save()


# newsletter
@socketio.on("newsletter_update")
def newsletter_update(data):
    passenger_id = current_user.id
    subscribe = data["subscribe"]

    passenger = storage.get_item("passenger", passenger_id)
    if passenger:
        print("updating passenger newsletter")
        passenger.newsletter = subscribe
        print(passenger.newsletter)
        storage.save()


# delete account
@socketio.on("delete-passenger-account")
def delete_passenger(data):
    passenger = storage.get_item("passenger", current_user.id)

    delete = data["clicked"]
    if type(delete) == bool:
        if delete:
            if passenger.profile_pic != "default.jpg":
                path_to_pic = os.path.join(
                    current_app.config["UPLOADED_PHOTOS_DEST"], passenger.profile_pic
                )
                if os.path.exists(path_to_pic):
                    os.remove(path_to_pic)
            logout_user()
            storage.delete_item("passenger", passenger.id)
            storage.save()
