from flask import Blueprint, render_template, flash
from src.models.passenger import Passenger
from src.models.driver import Driver
from src.models.vehicle import Vehicle
from ...forms.admin import addVehiclesForm
from src import db


admin_views = Blueprint("admin_views", __name__, url_prefix="/admin")


@admin_views.route("/", methods=["GET", "POST"])
def home():
    form = addVehiclesForm()
    passengers = Passenger.query.all()
    drivers = Driver.query.all()
    vehicles = Vehicle.query.all()
    if form.validate_on_submit():
        type = form.type.data

        type_exists = Vehicle.query.filter_by(type=type)
        if not type_exists:
            add_vehicle = Vehicle(type=type_exists)
            db.session.add(add_vehicle)
            db.session.commit()
        else:
            flash("Type exists", "error")

    return render_template(
        "admin/home.html",
        passengers=passengers,
        drivers=drivers,
        vehicles=vehicles,
        form=form,
    )


@admin_views.route("/drivers", methods=["GET", "POST"])
def get_drivers():
    render_template("admin/drivers.html")


@admin_views.route("/drivers", methods=["GET", "POST"])
def del_driver(id):
    driver_id = Driver.query.filter_by(id)
    if driver_id:
        db.session.delete(driver_id)
        db.session.commit()
    render_template("admin/drivers.html")
