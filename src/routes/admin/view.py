from flask import Blueprint, render_template, flash
from src.models.passenger import Passenger
from src.models.driver import Driver
from src.models.vehicle import Vehicle
from ...forms.admin import addVehiclesForm
from src import db
from ...models.engine import storage


admin_views = Blueprint("admin_views", __name__, url_prefix="/admin")


@admin_views.route("/", methods=["GET", "POST"])
def home():
    return render_template("admin/index.html")


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
