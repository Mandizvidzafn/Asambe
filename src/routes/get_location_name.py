import os
from dotenv import load_dotenv
import googlemaps
import json


def location_name(latitude, longitude):
    load_dotenv()
    api_key = os.getenv("MAPS_API_KEY")
    gmaps = googlemaps.Client(key=api_key)
    reverse_geocode_result = gmaps.reverse_geocode((latitude, longitude))

    if reverse_geocode_result:
        for result in reverse_geocode_result:
            for component in result["address_components"]:
                if "sublocality" in component["types"]:
                    return component["long_name"]
        return "Location name not found."
    else:
        return "Location name not found."
