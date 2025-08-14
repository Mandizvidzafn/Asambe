from flask import Blueprint, render_template, flash, request, redirect
from flask_login import current_user, login_required
from src.forms.feedback import FeedbackForm
from flask_mail import Message

views = Blueprint("views", __name__, url_prefix="/")


@views.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@views.route("/home", methods=["GET", "POST"])
def home():
    return render_template("ho.html")

@views.route("/dummy", methods=["GET", "POST"])
def ho():
    return render_template("ho.html")


@views.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    form = FeedbackForm()
    if request.method == "GET":
        form.name.data = current_user.firstname + " " + current_user.lastname
        form.phone.data = current_user.phone

    if form.validate_on_submit():
        name = form.name.data
        phone = form.name.data
        email = form.email.data
        message = form.message.data
        subject = form.subject.data

    return render_template("feedback.html", form=form)


@views.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("spDriver-Passenger.html")
