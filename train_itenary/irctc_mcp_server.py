import requests
import os
from typing import Any, Dict, List, Optional
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv
from itenary_builder import find_routes
from datetime import date
from train_graph_builder import build_train_graph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv(override=True)
logger = logging.getLogger(__name__)

mcp = FastMCP("IRCTC MCP Server")

API_ROOT = "https://railradar.in/api/v1"

route_cache = {}
station_cache = {}
train_graph = {}

# @mcp.tool()
# def get_station_code(station_name: str):
#     """Get the station code for a given station name."""

#     # add the logic to check if station name matches with station code. if so, return the station code in caps
#     if station_name in station_cache.values():
#         return station_name.upper()

#     # first search for exact match
#     for code, name in station_cache.items():
#         if name.lower() == station_name.lower():
#             logger.info(f"Found station code: {code} for station name: {station_name}")
#             return code
    
#     # then search for partial match
#     for code, name in station_cache.items():
#         if name.lower() in station_name.lower() or station_name.lower() in name.lower():
#             logger.info(f"Found station code: {code} for station name: {station_name}")
#             return code
#     logger.info(f"Station code not found for station name: {station_name}")
#     return None


@mcp.tool()
def search_stations(station_code_or_name: str):  
    """Search for railway stations by station code or name.
    
    This function queries the RailRadar API to find railway stations matching
    the provided search query. It can search by either station code (e.g., "NDLS")
    or station name (e.g., "New Delhi").
    
    Args:
        station_code_or_name (str): The station code or partial/full station name
            to search for. Examples: "NDLS", "Delhi", "Mumbai".
    
    Returns:
        dict: A JSON response containing a list of matching stations with their
            details including station code, name, and other metadata.
    """
    logger.info(f"Searching for station: {station_code_or_name}")
    response = requests.get(
        f"{API_ROOT}/search/stations",
        params={
            "q": station_code_or_name,
            "provider": "railradar"
        }
    )
    all_stations = response.json()["data"]["stations"]
    logger.info(f"trying exact match for {station_code_or_name}")
    for station in all_stations:        
        if station["code"].lower() in station_code_or_name.lower() or station_code_or_name.lower() in station["code"].lower():
            return station["code"].upper()

        if station["name"].lower() == station_code_or_name.lower():
            return station["code"].upper()

    logger.info(f"trying approx match for {station_code_or_name}")
    for station in all_stations:
        if station["name"].lower() in station_code_or_name.lower() or station_code_or_name.lower() in station["name"].lower():
            return station["code"].upper()
    return None


@mcp.tool()
def search_trains(train_nuber_name: str):
    """Search for trains by train number or train name.
    
    This function queries the RailRadar API to find trains matching the provided
    search query. It can search by either train number (e.g., "12345") or
    train name (e.g., "Rajdhani").
    
    Args:
        train_nuber_name (str): The train number or partial/full train name
            to search for. Examples: "12345", "Rajdhani", "Shatabdi".
    
    Returns:
        dict: A JSON response containing a list of matching trains with their
            details including train number, name, route, and schedule information.
    """
    logger.info(f"Searching for train: {train_nuber_name}")
    response = requests.get(
    f"{API_ROOT}/search/trains",
    params={
      "q": train_nuber_name
    }
)
    return response.json()


@mcp.tool()
def live_station_status(station_code: str):
    """Get live departure status for a railway station.
    
    This function retrieves real-time information about train departures from
    a specified railway station for the next 8 hours. It shows which trains
    are currently at the station or scheduled to depart soon.
    
    Args:
        station_code (str): The station code for which to retrieve live status.
            Example: "NDLS" for New Delhi, "BCT" for Mumbai Central.
    
    Returns:
        dict: A JSON response containing live departure information including
            train numbers, names, scheduled and expected departure times,
            platform numbers, and current status.
    """
    logger.info(f"Getting live departure status for station: {station_code}")
    response = requests.get(
    f"{API_ROOT}/stations/{station_code}/live",
    params={
      "hours": "8",
      "toStationCode": "",
      "type": "departures"
    }
)
    return response.json()


@mcp.tool()
def train_between_stations(from_station_code: str, to_station_code: str, max_hops: int = 3):
    """Find all trains running between two railway stations.
    
    This function queries the RailRadar API to retrieve a list of all trains
    that operate between the specified source and destination stations.
    
    Args:
        from_station_code (str): The station code of the departure/source station.
            Example: "NDLS" for New Delhi.
        to_station_code (str): The station code of the arrival/destination station.
            Example: "SDL" for Shahdol.
        max_hops (int): The maximum number of hops to consider when finding routes.
            Example: 3 for a maximum of 3 hops.
    
    Returns:
        dict: A JSON response containing a list of trains running between the
            two stations, including train numbers, names, departure and arrival
            times, journey duration, and days of operation.
    """

    journey_date = date.today().isoformat()

    logger.info(f"Getting trains between stations: {from_station_code} and {to_station_code} with max hops: {max_hops} journey date: {journey_date}")

    cache_key = f"{from_station_code}_{to_station_code}_{max_hops}"

    if route_cache.get(cache_key):
        return route_cache[cache_key]

    routes = find_routes(from_station=from_station_code, to_station=to_station_code, 
                         max_hops=max_hops, journey_date=journey_date, graph=train_graph)

    route_cache[cache_key] = routes

    return routes
    


@mcp.tool()
def get_train_data(train_number: str, journey_date: str):
    """Get detailed information about a specific train.
    
    This function queries the RailRadar API to retrieve comprehensive information
    about a specific train, including its schedule, stops, and other details.
    
    Args:
        train_number (str): The train number to retrieve information for.
            Example: "12345" for a specific train.
        journey_date (str): The journey date in the format YYYY-MM-DD for which to retrieve train information.
            Example: "2023-10-01" for a specific date.
    
    Returns:
        dict: A JSON response containing detailed information about the train,
            including its schedule, stops, and other relevant details.
    """
    logger.info(f"Getting train data for train: {train_number} for journey date: {journey_date}")
    response = requests.get(
    f"{API_ROOT}/trains/{train_number}",
    params={
      "journeyDate": journey_date,
      "dataType": "full",
      "provider": "railradar",
      "userId": ""
    }
)
    return response.json()

@mcp.tool()
def get_train_schedule(train_number: str, journey_date: str):   
    """Get the schedule of a specific train.
    
    This function queries the RailRadar API to retrieve the schedule of a specific train,
    including its stops and other details.
    
    Args:
        train_number (str): The train number to retrieve information for.
            Example: "12345" for a specific train.
        journey_date (str): The journey date in the format YYYY-MM-DD for which to retrieve train information.
            Example: "2023-10-01" for a specific date.
    
    Returns:
        dict: A JSON response containing the schedule of the train,
            including its stops and other relevant details.
    """
    logger.info(f"Getting train schedule for train: {train_number} for journey date: {journey_date}")
    response = requests.get(
    f"{API_ROOT}/trains/{train_number}/schedule",
    params={
      "journeyDate": journey_date
    }
)
    return response.json()


def load_stations():
    response = requests.get(
    f"{API_ROOT}/stations/all-kvs"
)
    all_stations = response.json()["data"]
    for station in all_stations:
        station_cache[station[0]] = station[1]
    
    logger.info(f"Loaded {len(station_cache)} stations")

def create_train_graph():
    journey_date = date.today().isoformat()
    train_graph.update(build_train_graph(journey_date, max_trains=500))
    logger.info(f"Updated train graph with {len(train_graph)} nodes")

if __name__ == "__main__":
    #load_stations()
    
    create_train_graph()

    mcp.run(transport="streamable-http", host="127.0.0.1", port=8282)
    #find_all_routes("NDLS", "BSB", "2025-12-15", max_hops=4)
