import googlemaps
from datetime import datetime
from dotenv import load_dotenv
import os
from fastmcp import FastMCP


load_dotenv(override=True)

def get_gmap_address(address: str) -> dict:
    """
    Validate and geocode an address using Google Maps Address Validation API.

    This function takes a raw address string and validates it against Google Maps
    Address Validation API, returning detailed information including the standardized
    address format and geographic coordinates (latitude/longitude).

    Args:
        address (str): The raw address string to validate and geocode.
                      Example: "some address"

    Returns:
        dict: A dictionary containing the address validation result with:
            - result.verdict: Validation verdict and quality indicators
            - result.address: Standardized address components
            - result.geocode: Geographic coordinates (lat/lng)
            - result.metadata: Additional metadata about the address

    Raises:
        googlemaps.exceptions.ApiError: If the API request fails
        ValueError: If GOOGLE_MAPS_API_KEY environment variable is not set

    Example:
        >>> result = get_gmap_address("some address")
        >>> lat = result['result']['geocode']['location']['latitude']
        >>> lng = result['result']['geocode']['location']['longitude']
    """
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))

    addressvalidation_result =  gmaps.addressvalidation([address], 
                                                        regionCode='IN',                                                    
                                                        enableUspsCass=False)
    #print(addressvalidation_result)
    lat = addressvalidation_result['result']['geocode']['location']['latitude']
    lng = addressvalidation_result['result']['geocode']['location']['longitude']
    print(f"get_gmap_address :: lat: {lat}, lng: {lng}")
    return lat, lng


def get_gmap_route(source_lat: float, source_lng: float, destination_lat: float, destination_lng: float) -> dict:
    """
    Get the route between two coordinates using Google Maps Directions API.

    Args:
        source_lat (float): Latitude of the starting point.
        source_lng (float): Longitude of the starting point.
        destination_lat (float): Latitude of the destination point.
        destination_lng (float): Longitude of the destination point.

    Returns:
        dict: Directions result containing route legs, steps, duration, and distance.
    """
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API_KEY'))
    now = datetime.now()
    directions_result = gmaps.directions((source_lat, source_lng),
                                         (destination_lat, destination_lng),
                                         mode="transit",
                                         departure_time=now)
    print(f"get_gmap_route :: directions_result: {directions_result}")
    return directions_result


def create_google_maps_route_link(origin, destination, waypoints=None):
    """
    Generates a Google Maps URL for directions.

    Args:
        origin (str): The starting point (address or lat/lng coordinates).
        destination (str): The ending point (address or lat/lng coordinates).
        waypoints (list of str, optional): A list of intermediate stops.

    Returns:
        str: A clickable URL that opens Google Maps with the route.
    """
    base_url = "https://www.google.com/maps/dir/?api=1"
    
    params = {
        "origin": origin,
        "destination": destination
    }
    
    if waypoints:
        params["waypoints"] = "|".join(waypoints)
        
    # URL-encode the parameters
    encoded_params = urllib.parse.urlencode(params)
    
    return f"{base_url}&{encoded_params}"



def compute_route(
    origin_lat: float, 
    origin_lng: float, 
    destination_lat: float, 
    destination_lng: float,
) -> dict:
    """
    Compute a route between two coordinates using Google Routes API v2.

    Args:
        origin_lat (float): Latitude of the starting point.
        origin_lng (float): Longitude of the starting point.
        destination_lat (float): Latitude of the destination point.
        destination_lng (float): Longitude of the destination point.        

    Returns:
        dict: Route response containing duration, distance, and encoded polyline.
    """
    import requests

    url = "https://routes.googleapis.com/directions/v2:computeRoutes"
   
    travel_mode: str = "DRIVE"
    routing_preference: str = "TRAFFIC_AWARE"
    avoid_tolls: bool = False
    avoid_highways: bool = False
    avoid_ferries: bool = False

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": os.getenv("GOOGLE_MAPS_API_KEY"),
        "X-Goog-FieldMask": "routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline"
    }
    
    payload = {
        "origin": {
            "location": {
                "latLng": {
                    "latitude": origin_lat,
                    "longitude": origin_lng
                }
            }
        },
        "destination": {
            "location": {
                "latLng": {
                    "latitude": destination_lat,
                    "longitude": destination_lng
                }
            }
        },
        "travelMode": travel_mode,
        "routingPreference": routing_preference,
        "computeAlternativeRoutes": False,
        "routeModifiers": {
            "avoidTolls": avoid_tolls,
            "avoidHighways": avoid_highways,
            "avoidFerries": avoid_ferries
        },
        "languageCode": "en-US",
        "units": "METRIC",
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    print(f"route result: {result}")
    return result

def open_map_viewer(polyline: str) -> str:
    """
    Open the map viewer in a browser with the given polyline displayed.

    Args:
        polyline (str): The encoded polyline string from Google Routes API.

    Returns:
        str: Success message indicating the map was opened.
    """
    import webbrowser
    import urllib.parse

    print(f"will map viewer with polyline: {polyline}")
    
    # Get the API key from environment
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # Get the path to map_viewer.html
    current_dir = os.path.dirname(os.path.abspath(__file__))
    map_viewer_path = os.path.join(current_dir, "map_viewer.html")
    
    # Create a URL with the polyline and API key as query parameters
    file_url = f"file:///{map_viewer_path.replace(os.sep, '/')}?polyline={urllib.parse.quote(polyline)}&apikey={api_key}"
    
    # Open in default browser
    webbrowser.open(file_url)
    
    return f"Map viewer opened in browser with url {file_url}"

