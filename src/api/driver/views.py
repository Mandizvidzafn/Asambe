from flask_restx import Namespace, Resource, fields
from flask import request,Blueprint, jsonify
from http import HTTPStatus
from ...models.engine import storage
#from ...models.driver import Driver


driver_views_ns = Namespace("driver", description="All views for  drivers")

all_drivers_model = driver_views_ns.model (
    "All Drivers", 
    {
        "id": fields.Integer(),
        "firstname": fields.String(),
        "lastname": fields.String(),
        "vehicle_type": fields.String(),
        "location": fields.String()
    }
)

driver_active_model = driver_views_ns.model(
    "Change Active status",
    {
        "active": fields.Boolean(description="the status you want to change to", required=1)
    }
)

@driver_views_ns.route("/")
class DriverApi(Resource):
    """
    Driver home api views
    """

    @driver_views_ns.marshal_list_with(all_drivers_model)
    def get(self):
        """ return a list for all drivers """

        drivers = storage.all("driver")
        #drivers = Driver.query.all()
        return drivers, HTTPStatus.OK


@driver_views_ns.route("/<int:id>")
class DriverById(Resource):

    @driver_views_ns.marshal_with(all_drivers_model)
    def get(self,id):
        """
        Get a driver by id
        """
        driver = storage.get_item("driver",id)
        if driver:
            return driver, HTTPStatus.OK
        return jsonify("error: id not found"), HTTPStatus.NOT_FOUND

    @driver_views_ns.marshal_with(all_drivers_model)
    @driver_views_ns.expect(driver_active_model)
    def put(self,id):
        """
        Update driver details
        """
        data = request.json()
        driver = storage.get_item("driver",id)
        if driver:
            if "active" in data:
                print(True)
                driver.active = data["active"]
                storage.save()

        return driver, HTTPStatus.OK

@driver_views_ns.route("/active")
class driverActive(Resource):
    """
    Active driver operations
    """
    @driver_views_ns.marshal_list_with(all_drivers_model)
    def get(self):
        """
        get all active drivers
        """

        drivers = storage.get_all_filtered_item("driver", "active", True)

        return drivers, HTTPStatus.OK