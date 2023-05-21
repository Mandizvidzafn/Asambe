from flask import Blueprint, render_template, url_for, redirect
from ...forms.admin import SigninForm

admin_auth = Blueprint("admin_auth", __name__, url_prefix="/admin")


@admin_auth.route("/signin", methods=["GET", "POST"])
def signin():
    form = SigninForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

    return render_template("admin/signin.html", form=form)
