"""views.py"""
from flask import redirect, render_template, request, Blueprint, url_for
from src.forms.driver import SignupForm, SigninForm, UpdateForm
from src.models.driver import Driver
from src import db
from flask_login import current_user, user_logged_in
from ..multiple_login_required import login_required_with_manager
from src import driver_login_manager


driver_views = Blueprint("driver_views", __name__, url_prefix="/driver")


@driver_views.route("/")
@driver_views.route("/home", methods=["GET", "POST"])
@login_required_with_manager(driver_login_manager)
def home():
    if not current_user.is_authenticated:
        return redirect(url_for("driver_auth.signin"))
    print(f"current user id is {current_user.id}")
    return render_template("driver/index.html", user=current_user)


@driver_views.route("/profile", methods=["GET", "POST"])
@login_required_with_manager(driver_login_manager)
def profile():
    form = UpdateForm()
    if request.method == "GET":
        form.firstname.data = current_user.firstname
        form.lastname.data = current_user.lastname
        form.phone.data = current_user.phone
    return render_template("driver/profile.html", user=current_user, form=form)
