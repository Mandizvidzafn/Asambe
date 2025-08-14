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
from src.forms.driver import (
    SigninForm,
    SignupForm,
    ForgotPasswordForm,
    VerifyOTPForm,
    UpdateForm,
)
from src.models.driver import Driver
from src.models.vehicle import Vehicle
from src import db, socketio, photos
from flask_socketio import emit
from flask_bcrypt import check_password_hash, generate_password_hash
from twilio.rest import Client
from dotenv import load_dotenv
import os
from ..get_location_name import location_name
from ...models.engine import storage
from ..generate_ids import generate_driver_id
from uuid import uuid4
from werkzeug.utils import secure_filename
from PIL import Image

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
    # phone_intl = request.form.get("phone-intl")

    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        vehicle_type = form.vehicle.data
        newsletter = form.newsletter.data
        password = form.password.data
        phone = form.phone.data
        confirm_password = form.confirm_password.data

        vehicle_id = Vehicle.query.get(vehicle_type)

        hashed_password = generate_password_hash(password, rounds=12)
        print(f"vehicle type is {vehicle_type}")
        print(f"phone: {phone}")
        user = storage.get_filtered_item("driver", "phone", phone)
        if user:
            form.phone.errors.append("Phone number exists")

        elif password != confirm_password:
            print("not equal")
            form.password.errors.append("passwords must match")
            form.confirm_password.errors.append("passwords must match")
        elif len(password) < 7:
            form.password.errors.append("password must be 7 or more characters")
        else:
            session["phone"] = phone
            session["vehicle_id"] = vehicle_id
            session["lastname"] = lastname
            session["firstname"] = firstname
            session["newsletter"] = newsletter
            session["password"] = hashed_password
            send_otp = client.verify.v2.services(verify_sid).verifications.create(
                to=phone, channel="sms"
            )
            if send_otp.sid:
                return redirect(url_for("driver_auth.signup_verify_otp"))
    return render_template("driver/signup.html", form=form)


@driver_auth.route("/signup_verify_otp", methods=["GET", "POST"])
def signup_verify_otp():
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
            vehicle_id = session.get("vehicle_id")
            lastname = session.get("lastname")
            firstname = session.get("firstname")
            newsletter = session.get("newsletter")
            hashed_password = session.get("password")

            verify_otp_code = client.verify.services(
                verify_sid
            ).verification_checks.create(to=phone, code=otp_int)
            if verify_otp_code.status == "approved":
                new_user = Driver(
                    lastname=lastname,
                    firstname=firstname,
                    phone=phone,
                    vehicle_type=vehicle_id,
                    newsletter=newsletter,
                    password=hashed_password,
                )
                storage.create(new_user)
                storage.save()
                session.clear()
                login_user(new_user, remember=True)
                return redirect(url_for("driver_views.home"))
            else:
                flash("Wrong OTP")
    return render_template("driver/verify_otp.html", form=form)


@driver_auth.route("/retrieve-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("driver_views.home"))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        phone_intl = form.phone.data
        existing_driver = storage.get_filtered_item("driver", "phone", phone_intl)
        if existing_driver:
            session["phone"] = phone_intl
            send_otp = client.verify.v2.services(reset_sid).verifications.create(
                to=phone_intl, channel="sms"
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
            form.otp.errors.append("OTP should contain only numbers")
            return render_template("passenger/verify_otp.html", form=form)
        if len(str(otp_int)) != 6:
            form.otp.errors.append("OTP must be only 6 digits")
            phone = session.get("phone")
            verify_otp_code = client.verify.services(
                reset_sid
            ).verification_checks.create(to=phone, code=otp_int)
            if verify_otp_code.status == "approved":
                session.clear()
                existing_driver = storage.get_filtered_item("driver", "phone", phone)
                login_user(existing_driver)
                return redirect(url_for("driver_views.home"))
            else:
                flash("Wrong OTP")
    return render_template("driver/verify_otp.html", form=form)


@driver_auth.route("/profile", methods=["GET", "POST", "PATCH"])
@login_required
def profile():
    if current_user.role == "passenger":
        return redirect(url_for("passenger_auth.profile"))
    form = UpdateForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        phone = form.phone.data
        confirm_password = form.confirm_password.data
        password = form.password.data
        pic = form.profile_image.data
        user = storage.get_item("driver", current_user.id)
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
                    check_phone = storage.get_filtered_item("driver", "phone", phone)
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
                    "Invalid file formattt. Only JPEG and PNG are allowed"
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

    if request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone

    image = url_for("static", filename="img/" + current_user.profile_pic)

    return render_template(
        "driver/profile.html", user=current_user, form=form, image=image
    )


@driver_auth.route("/logout", methods=["GET", "POST"])
@login_required
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
        storage.save()

        if not status:
            emit("remove_inactive_drivers", {"driver_ids": [driver_id]}, broadcast=True)

    emit("status_update", {"status": status}, broadcast=True)


# transport type update
@socketio.on("vehicle_update")
def handle_vehicle_update(data):
    driver_id = current_user.id
    trans = data["selectedId"]

    driver = storage.get_item("driver", driver_id)
    if driver:
        print("updating driver vehicle")
        driver.vehicle_type = trans
        db.session.commit()

        print(f"drivers vehicle is {current_user.vehicle_type}")


# delete account
@socketio.on("delete-driver-account")
def delete_driver(data):
    driver = storage.get_item("driver", current_user.id)

    delete = data["clicked"]
    if type(delete) == bool:
        if delete:
            if driver.profile_pic != "default.jpg":
                path_to_pic = os.path.join(
                    current_app.config["UPLOADED_PHOTOS_DEST"], driver.profile_pic
                )
                if os.path.exists(path_to_pic):
                    os.remove(path_to_pic)
            logout_user()
            storage.delete_item("driver", driver.id)
            storage.save()
