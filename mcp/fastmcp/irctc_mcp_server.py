import requests
import os
from typing import Any, Dict, List, Optional
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv(override=True)
logger = logging.getLogger(__name__)

#mcp = FastMCP("IRCTC MCP Server")

API_ROOT = "https://railradar.in/api/v1"

#@mcp.tool()
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
    return response.json()

#@mcp.tool()
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

#@mcp.tool()
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


#@mcp.tool()
def train_between_stations(from_station_code: str, to_station_code: str):
    """Find all trains running between two railway stations.
    
    This function queries the RailRadar API to retrieve a list of all trains
    that operate between the specified source and destination stations.
    
    Args:
        from_station_code (str): The station code of the departure/source station.
            Example: "NDLS" for New Delhi.
        to_station_code (str): The station code of the arrival/destination station.
            Example: "SDL" for Shahdol.
    
    Returns:
        dict: A JSON response containing a list of trains running between the
            two stations, including train numbers, names, departure and arrival
            times, journey duration, and days of operation.
    """
    logger.info(f"Getting trains between stations: {from_station_code} and {to_station_code}")
    response = requests.get(
    f"{API_ROOT}/trains/between",
    params={
      "from": from_station_code,
      "to": to_station_code
    }
)
    return response.json()


#@mcp.tool()
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

#@mcp.tool()
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


#@mcp.tool()
def find_all_routes(from_station_code: str, to_station_code: str, journey_date: str, 
                    min_layover_minutes: int = 30, max_layover_hours: int = 6,
                    max_hops: int = 1) -> Dict[str, Any]:
    """Find all possible train routes (direct and multi-hop) between two stations.
    
    Uses a graph-based DFS approach to find all paths, then validates time constraints
    for multi-hop routes to ensure proper layovers with no overlapping times.
    
    Args:
        from_station_code (str): The station code of the departure/source station.
            Example: "NDLS" for New Delhi.
        to_station_code (str): The station code of the arrival/destination station.
            Example: "BCT" for Mumbai Central.
        journey_date (str): The journey date in the format YYYY-MM-DD.
            Example: "2025-11-25".
        min_layover_minutes (int, optional): Minimum layover time required at 
            intermediate stations in minutes. Defaults to 30 minutes.
        max_layover_hours (int, optional): Maximum layover time allowed at 
            intermediate stations in hours. Defaults to 6 hours.
        max_hops (int, optional): Maximum number of hops/transfers allowed. 
            Defaults to 1 (one transfer, i.e., two trains).
    
    Returns:
        dict: A structured response containing direct trains, multi-hop routes, and summary.
    """
    from datetime import datetime, timedelta
    
    logger.info(f"Finding all routes from {from_station_code} to {to_station_code} on {journey_date}")
    
    result = {
        "direct_trains": [],
        "multi_hop_routes": [],
        "summary": {}
    }
    
    # Step 1: Build a graph of train connections
    graph = _build_train_graph(from_station_code, to_station_code, max_hops, journey_date)
    
    # Step 2: Find all paths using DFS
    all_paths = []
    visited = set()
    current_path = []
    
    _dfs_find_paths(graph, from_station_code, to_station_code, visited, current_path, all_paths, max_hops)
    
    logger.info(f"Found {len(all_paths)} potential paths using DFS")
    
    # Step 3: Process paths and validate time constraints
    for path in all_paths:
        if len(path) == 1:
            # Direct connection
            station_pair = path[0]
            trains_data = graph.get(station_pair, [])
            
            for train in trains_data:
                journey_seg = train.get("journeySegment", {})
                result["direct_trains"].append({
                    "train_number": train.get("number"),
                    "train_name": train.get("name"),
                    "from_station": from_station_code,
                    "to_station": to_station_code,
                    "departure_time": journey_seg.get("departureTime"),
                    "arrival_time": journey_seg.get("arrivalTime"),
                    "duration": journey_seg.get("travelTime"),
                    "days_of_operation": train.get("runDays", [])
                })
        else:
            # Multi-hop route - validate time constraints
            valid_routes = _validate_multihop_route(
                path, graph, journey_date, min_layover_minutes, max_layover_hours
            )
            result["multi_hop_routes"].extend(valid_routes)
    
    result["summary"]["total_direct_trains"] = len(result["direct_trains"])
    result["summary"]["total_multi_hop_routes"] = len(result["multi_hop_routes"])
    result["summary"]["total_routes"] = result["summary"]["total_direct_trains"] + result["summary"]["total_multi_hop_routes"]
    
    logger.info(f"Found {result['summary']['total_direct_trains']} direct trains and {result['summary']['total_multi_hop_routes']} multi-hop routes")
    
    return result


def _build_train_graph(from_station: str, to_station: str, max_hops: int, journey_date: str) -> Dict[tuple, List[Dict]]:
    """Build a graph of train connections by dynamically discovering intermediate stations.
    
    Instead of hardcoding junctions, this discovers intermediate stations by:
    1. Getting trains from source and examining their schedules
    2. Getting trains to destination and examining their schedules
    3. Using discovered stations as potential intermediate points
    
    Args:
        from_station: Source station code
        to_station: Destination station code
        max_hops: Maximum number of hops to explore
        journey_date: Journey date for getting train schedules
    
    Returns:
        Graph as dict with (from, to) tuples as keys and list of trains as values
    """
    from collections import defaultdict
    
    graph = defaultdict(list)
    explored_stations = set()
    candidate_intermediates = set()
    
    # Step 1: Try direct connection and discover intermediate stations
    try:
        response = train_between_stations(from_station, to_station)
        if response.get("data") and response["data"].get("trains"):
            trains = response["data"]["trains"]
            graph[(from_station, to_station)] = trains
            logger.info(f"Found {len(trains)} direct trains: {from_station} → {to_station}")
            
            # Discover intermediate stations from these direct trains' schedules
            if max_hops > 0:
                for train in trains[:5]:  # Limit to first 5 trains to avoid too many API calls
                    intermediate_stops = _get_intermediate_stations_from_train(
                        train.get("number"), journey_date, from_station, to_station
                    )
                    candidate_intermediates.update(intermediate_stops)
                    
                logger.info(f"Discovered {len(candidate_intermediates)} potential intermediate stations from direct trains")
    except Exception as e:
        logger.warning(f"Error getting direct trains: {e}")
    
    # Step 2: Build graph with discovered intermediate stations
    if max_hops > 0 and candidate_intermediates:
        explored_stations.add(from_station)
        
        # Try connections from source to intermediate stations
        for intermediate in candidate_intermediates:
            if intermediate not in explored_stations:
                try:
                    response = train_between_stations(from_station, intermediate)
                    if response.get("data") and response["data"].get("trains"):
                        trains = response["data"]["trains"]
                        graph[(from_station, intermediate)] = trains
                        logger.info(f"Found {len(trains)} trains: {from_station} → {intermediate}")
                except Exception as e:
                    logger.debug(f"No trains from {from_station} to {intermediate}")
        
        # Try connections from intermediate stations to destination
        for intermediate in candidate_intermediates:
            if intermediate not in explored_stations:
                try:
                    response = train_between_stations(intermediate, to_station)
                    if response.get("data") and response["data"].get("trains"):
                        trains = response["data"]["trains"]
                        graph[(intermediate, to_station)] = trains
                        logger.info(f"Found {len(trains)} trains: {intermediate} → {to_station}")
                except Exception as e:
                    logger.debug(f"No trains from {intermediate} to {to_station}")
    
    return dict(graph)


def _get_intermediate_stations_from_train(train_number: str, journey_date: str, 
                                          exclude_from: str, exclude_to: str) -> set:
    """Get intermediate station codes from a train's route data.
    
    Uses get_train_data API to retrieve comprehensive train information including
    all intermediate stops with proper day tracking.
    
    Args:
        train_number: Train number to get data for
        journey_date: Journey date
        exclude_from: Source station to exclude
        exclude_to: Destination station to exclude
    
    Returns:
        Set of intermediate station codes
    """
    intermediate_stations = set()
    
    try:
        response = get_train_data(train_number, journey_date)
        
        if response.get("data") and response["data"].get("route"):
            route = response["data"]["route"]
            
            # Extract station codes from route
            for stop in route:
                station_code = stop.get("stationCode")
                if station_code and station_code not in [exclude_from, exclude_to]:
                    intermediate_stations.add(station_code)
                    
            logger.debug(f"Train {train_number} has {len(intermediate_stations)} intermediate stops")
                    
    except Exception as e:
        logger.debug(f"Could not get data for train {train_number}: {e}")
    
    return intermediate_stations


def _dfs_find_paths(graph: Dict, current: str, destination: str, visited: set, 
                    path: List, all_paths: List, max_hops: int):
    """DFS to find all paths from current station to destination.
    
    Args:
        graph: Train connection graph
        current: Current station code
        destination: Destination station code
        visited: Set of visited stations (to avoid cycles)
        path: Current path of (from, to) tuples
        all_paths: Accumulator for all found paths
        max_hops: Maximum hops allowed
    """
    if len(path) > max_hops:
        return
    
    # Check direct connection to destination
    if (current, destination) in graph:
        all_paths.append(path + [(current, destination)])
    
    # Explore further if under max hops
    if len(path) < max_hops:
        visited.add(current)
        
        for (from_st, to_st) in graph.keys():
            if from_st == current and to_st not in visited and to_st != destination:
                _dfs_find_paths(graph, to_st, destination, visited, 
                              path + [(from_st, to_st)], all_paths, max_hops)
        
        visited.remove(current)


def _validate_multihop_route(path: List[tuple], graph: Dict, journey_date: str,
                             min_layover_minutes: int, max_layover_hours: int) -> List[Dict]:
    """Validate multi-hop routes for proper layover times and build route details.
    
    Args:
        path: List of (from, to) station pairs
        graph: Graph with train data
        journey_date: Journey date string
        min_layover_minutes: Minimum layover in minutes
        max_layover_hours: Maximum layover in hours
    
    Returns:
        List of valid multi-hop routes with complete details
    """
    from datetime import datetime, timedelta
    from itertools import product
    
    # Get train options for each leg
    leg_train_options = []
    for station_pair in path:
        trains = graph.get(station_pair, [])
        if not trains:
            return []
        leg_train_options.append(trains)
    
    valid_routes = []
    
    # Try all train combinations
    for train_combo in product(*leg_train_options):
        is_valid, route_data = _validate_train_combination(
            train_combo, path, journey_date, min_layover_minutes, max_layover_hours
        )
        
        if is_valid:
            valid_routes.append(route_data)
    
    return valid_routes


def _validate_train_combination(trains: tuple, path: List[tuple], journey_date: str,
                                min_layover_min: int, max_layover_hrs: int):
    """Validate a specific combination of trains for time constraints.
    
    Returns:
        Tuple of (is_valid: bool, route_data: dict)
    """
    from datetime import datetime, timedelta
    
    legs = []
    prev_arrival = None
    journey_start = None
    
    for i, train in enumerate(trains):
        try:
            journey_seg = train.get("journeySegment", {})
            dep_str = journey_seg.get("departureTime", "")
            arr_str = journey_seg.get("arrivalTime", "")
            
            if not dep_str or not arr_str:
                return False, {}
            
            # Normalize time format
            if len(dep_str.split(":")) == 2:
                dep_str += ":00"
            if len(arr_str.split(":")) == 2:
                arr_str += ":00"
            
            dep_time = datetime.strptime(f"{journey_date} {dep_str}", "%Y-%m-%d %H:%M:%S")
            arr_time = datetime.strptime(f"{journey_date} {arr_str}", "%Y-%m-%d %H:%M:%S")
            
            # Handle overnight journeys
            if arr_time < dep_time:
                arr_time += timedelta(days=1)
            
            # Adjust for multi-day journeys
            if prev_arrival:
                while dep_time < prev_arrival:
                    dep_time += timedelta(days=1)
                    arr_time += timedelta(days=1)
                
                layover = dep_time - prev_arrival
                min_delta = timedelta(minutes=min_layover_min)
                max_delta = timedelta(hours=max_layover_hrs)
                
                if not (min_delta <= layover <= max_delta):
                    return False, {}
                
                layover_hrs = int(layover.total_seconds() // 3600)
                layover_min = int((layover.total_seconds() % 3600) // 60)
                layover_str = f"{layover_hrs}h {layover_min}m"
            else:
                layover_str = None
                journey_start = dep_time
            
            journey_seg = train.get("journeySegment", {})
            leg_info = {
                "leg_number": i + 1,
                "train_number": train.get("number"),
                "train_name": train.get("name"),
                "from_station": path[i][0],
                "to_station": path[i][1],
                "departure_time": journey_seg.get("departureTime"),
                "arrival_time": journey_seg.get("arrivalTime"),
                "duration": journey_seg.get("travelTime")
            }
            
            if layover_str:
                leg_info["layover_at_previous_station"] = layover_str
            
            legs.append(leg_info)
            prev_arrival = arr_time
            
        except Exception as e:
            logger.warning(f"Time validation error: {e}")
            return False, {}
    
    # Calculate total journey time
    if journey_start and prev_arrival:
        total_duration = prev_arrival - journey_start
        hrs = int(total_duration.total_seconds() // 3600)
        mins = int((total_duration.total_seconds() % 3600) // 60)
        
        intermediate_stations = [path[i][1] for i in range(len(path) - 1)]
        
        route_data = {
            "total_journey_time": f"{hrs}h {mins}m",
            "total_hops": len(path) - 1,
            "intermediate_stations": intermediate_stations,
            "legs": legs
        }
        
        return True, route_data
    
    return False, {}


if __name__ == "__main__":
    #mcp.run(transport="streamable-http", host="127.0.0.1", port=8282)
    find_all_routes("NDLS", "BSB", "2025-12-15", max_hops=4)
