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
            # json_output = json.dumps(result, indent=4)
            # print(json_output)
            for component in result["address_components"]:
                if "sublocality" in component["types"]:
                    return component["long_name"]
        return "Location name not found."
    else:
        return "Location name not found."


# Example usage
latitude = -33.9632036
longitude = 25.6126778
api_key = os.getenv("MAPS_API_KEY")
# Replace with your actual API key

location_name = location_name(latitude, longitude)
print(location_name)

output = {"location_name": location_name}

# Generate JSON output with 4 spaces indentation
