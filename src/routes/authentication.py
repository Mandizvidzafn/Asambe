from flask import Blueprint, render_template, request, session, redirect, flash, url_for
from flask_login import current_user, login_user, login_required, logout_user
from ..forms.signin import SigninForm
from ..models.engine import storage
from flask_bcrypt import check_password_hash
from urllib.parse import urlparse, urljoin

auth = Blueprint("auth", __name__, url_prefix="/signin")


@auth.route("/", methods=["GET", "POST"])
def signin():
    if current_user.is_authenticated:
        if current_user.role == "driver":
            return redirect(url_for("driver_views.home"))
        elif current_user.role == "passenger":
            return redirect(url_for("passenger_views.home"))
    else:
        form = SigninForm()
        phone = form.phone.data
        password = form.password.data

        if form.validate_on_submit():
            check_driver = storage.get_filtered_item("driver", "phone", phone)
            check_passenger = storage.get_filtered_item("passenger", "phone", phone)
            if check_driver:
                if check_password_hash(check_driver.password, password):
                    login_user(check_driver)
                    print(
                        f"current driver user is {current_user.phone} and authenticated"
                    )
                    print(f"current user role is {current_user.role}")
                    return redirect(url_for("driver_views.home"))

            elif check_passenger:
                if check_password_hash(check_passenger.password, password):
                    login_user(check_passenger)
                    if current_user.is_authenticated:
                        print(
                            f"current passenger user is {current_user.phone} and authenticated"
                        )
                        print(f"current user role is {current_user.role}")
                        return redirect(url_for("passenger_views.home"))
            else:
                flash("user doesnt exists")
    return render_template("signin.html", form=form)


@auth.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()
    logout_user()
    return redirect(url_for("auth.signin"))
