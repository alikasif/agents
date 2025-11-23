import requests
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_trains():
    """
    return all trains with train number and train name
    """
    response = requests.get("https://railradar.in/api/v1/trains/all-kvs")
    return response.json()


def get_train_data(train_number: str, journey_date: str):
    """
    given a train number and journey date, return the train data. it contains train number with full route information   
    """
    response = requests.get(
        f"https://railradar.in/api/v1/trains/{train_number}",
        params={
            "journeyDate": journey_date,
            "dataType": "full",
            "provider": "railradar",
            "userId": ""
        }
    )
    return response.json()


def build_train_graph(journey_date: str, max_trains: int = 500) -> Dict[Tuple[str, str], List[Dict]]:
    """
    Build a graph where stations are nodes and trains are edges.
    
    Args:
        journey_date: Journey date in YYYY-MM-DD format
        max_trains: Maximum number of trains to process (to limit API calls)
    
    Returns:
        Dictionary with (from_station, to_station) tuples as keys and list of trains as values
        Example: {("NDLS", "AGC"): [{train_number, train_name, departure_time, arrival_time, ...}]}
    """
    logger.info(f"Building train graph for {journey_date} (processing up to {max_trains} trains)")
    
    # Get all trains
    all_trains_response = get_all_trains()
    if not all_trains_response.get("success") or not all_trains_response.get("data"):
        logger.error("Failed to fetch all trains")
        return {}
    
    all_trains = all_trains_response["data"][:max_trains]
    logger.info(f"Processing {len(all_trains)} trains")
    
    # Build graph
    graph = defaultdict(list)
    processed = 0
    
    for train_entry in all_trains:
        train_number = train_entry[0]
        train_name = train_entry[1]
        
        try:
            # Get detailed route data for this train
            train_data = get_train_data(train_number, journey_date)
            
            if not train_data.get("data") or not train_data["data"].get("route"):
                continue
            
            route = train_data["data"]["route"]
            train_info = train_data["data"].get("train", {})
            
            # Extract edges (station-to-station connections) from the route
            for i in range(len(route) - 1):
                from_stop = route[i]
                to_stop = route[i + 1]
                
                from_station = from_stop.get("stationCode")
                to_station = to_stop.get("stationCode")
                
                if not from_station or not to_station:
                    continue
                
                # Create edge with train information
                edge = {
                    "train_number": train_number,
                    "train_name": train_name,
                    "from_station": from_station,
                    "from_station_name": from_stop.get("stationName"),
                    "to_station": to_station,
                    "to_station_name": to_stop.get("stationName"),
                    "departure_time": from_stop.get("scheduledDeparture"),  # epoch timestamp or None
                    "arrival_time": to_stop.get("scheduledArrival"),  # epoch timestamp or None
                    # "distance_km": to_stop.get("distanceFromSourceKm", 0) - from_stop.get("distanceFromSourceKm", 0),
                    # "from_day": from_stop.get("day", 1),
                    # "to_day": to_stop.get("day", 1),
                    # "running_days_bitmap": train_info.get("runningDaysBitmap"),
                }
                
                graph[(from_station, to_station)].append(edge)
                logger.info(f"Added edge {from_station} -> {to_station} with train {train_number} arrival time: {to_stop.get('scheduledArrival')} departure time: {from_stop.get('scheduledDeparture')}")
            
            processed += 1
            if processed % 50 == 0:
                logger.info(f"Processed {processed}/{len(all_trains)} trains")
                
        except Exception as e:
            logger.debug(f"Error processing train {train_number}: {e}")
            continue
    
    logger.info(f"Graph built with {len(graph)} unique station pairs from {processed} trains")
    return dict(graph)


def find_routes(
    from_station: str,
    to_station: str,
    journey_date: str,
    max_hops: int = 2,
    graph: Optional[Dict] = None,
    min_layover_minutes: int = 30,
    max_layover_minutes: int = 360
) -> Dict:
    """
    Find all routes (direct and multi-hop) between two stations.
    
    Args:
        from_station: Source station code
        to_station: Destination station code
        journey_date: Journey date in YYYY-MM-DD format
        max_hops: Maximum number of train changes allowed (default: 2)
        graph: Pre-built graph (if None, will build new one)
        min_layover_minutes: Minimum layover time at intermediate stations
        max_layover_minutes: Maximum layover time at intermediate stations
    
    Returns:
        Dictionary with direct_routes, multi_hop_routes, and summary
    """
    logger.info(f"Finding routes from {from_station} to {to_station} on {journey_date} (max {max_hops} hops)")
    
    # Build graph if not provided
    if graph is None:
        graph = build_train_graph(journey_date)
    
    # Find all paths using BFS
    all_paths = _find_all_paths_bfs(graph, from_station, to_station, max_hops)
    logger.info(f"Found {all_paths} possible paths")
    
    result = {
        "direct_routes": [],
        "multi_hop_routes": [],
        "summary": {}
    }
    
    # Process paths
    for path in all_paths:
        logger.info(f"Processing path {path} of length {len(path)}")

        if len(path) == 1:
            # Direct route
            from_st, to_st = path[0]
            trains = graph.get((from_st, to_st), [])
            logger.info(f"Found {trains} trains for direct route")

            for train in trains:
                result["direct_routes"].append({
                    "train_number": train["train_number"],
                    "train_name": train["train_name"],
                    "from_station": from_st,
                    "to_station": to_st,
                    "departure_time": _format_timestamp(train["departure_time"]),
                    "arrival_time": _format_timestamp(train["arrival_time"]),
                    #"from_day": train["from_day"],
                    #"to_day": train["to_day"]
                })
        else:
            # Multi-hop route - validate and build
            valid_routes = _build_multi_hop_routes(
                path, graph, journey_date, min_layover_minutes, max_layover_minutes
            )
            result["multi_hop_routes"].extend(valid_routes)
    
    result["summary"] = {
        "from_station": from_station,
        "to_station": to_station,
        "journey_date": journey_date,
        "total_direct_routes": len(result["direct_routes"]),
        "total_multi_hop_routes": len(result["multi_hop_routes"]),
        "total_routes": len(result["direct_routes"]) + len(result["multi_hop_routes"])
    }
    
    logger.info(f"Found {result['summary']['total_direct_routes']} direct and {result['summary']['total_multi_hop_routes']} multi-hop routes")
    return result


def _find_all_paths_bfs(
    graph: Dict[Tuple[str, str], List[Dict]],
    start: str,
    end: str,
    max_hops: int
) -> List[List[Tuple[str, str]]]:
    """
    Find all paths from start to end station using BFS with max_hops limit.
    
    Returns:
        List of paths, where each path is a list of (from_station, to_station) tuples
    """
    all_paths = []
    
    # BFS queue: (current_station, path_so_far, visited_stations)
    queue = deque([(start, [], set([start]))])
    
    while queue:
        current, path, visited = queue.popleft()
        
        # Check if we've exceeded max hops
        if len(path) > max_hops:
            continue
        
        # Check all outgoing edges from current station
        for (from_st, to_st), trains in graph.items():
            if from_st == current and trains:
                new_path = path + [(from_st, to_st)]
                
                # Found destination
                if to_st == end:
                    all_paths.append(new_path)
                    continue
                
                # Continue exploring if not visited and under hop limit
                if to_st not in visited and len(new_path) < max_hops:
                    new_visited = visited.copy()
                    new_visited.add(to_st)
                    queue.append((to_st, new_path, new_visited))
    
    return all_paths


def _build_multi_hop_routes(
    path: List[Tuple[str, str]],
    graph: Dict,
    journey_date: str,
    min_layover_min: int,
    max_layover_min: int
) -> List[Dict]:
    """
    Build valid multi-hop routes from a path by checking all train combinations.
    
    Returns:
        List of valid route dictionaries
    """
    from itertools import product
    
    # Get all train options for each leg
    leg_options = []
    for from_st, to_st in path:
        trains = graph.get((from_st, to_st), [])
        logger.info(f"Found {trains} trains for leg {from_st} -> {to_st}")
        if not trains:
            return []
        leg_options.append(trains)
    
    valid_routes = []
    
    # Try all combinations of trains
    for train_combination in product(*leg_options):
        route = _validate_train_combination(
            train_combination, path, journey_date, min_layover_min, max_layover_min
        )
        if route:
            valid_routes.append(route)
    
    return valid_routes


def _validate_train_combination(
    trains: Tuple[Dict],
    path: List[Tuple[str, str]],
    journey_date: str,
    min_layover_min: int,
    max_layover_min: int
) -> Optional[Dict]:
    """
    Validate a specific combination of trains for time constraints.
    
    Returns:
        Route dictionary if valid, None otherwise
    """
    legs = []
    prev_arrival_time = None
    prev_train_number = None
    total_start = None
    layover_str = None
    
    for i, train in enumerate(trains):
        dep_timestamp = train["departure_time"]
        arr_timestamp = train["arrival_time"]
        current_train_number = train["train_number"]
        
        if dep_timestamp is None or arr_timestamp is None:
            return None
        
        # Convert timestamps to datetime
        dep_time = datetime.fromtimestamp(dep_timestamp)
        arr_time = datetime.fromtimestamp(arr_timestamp)
        
        # For first leg, record start time
        if i == 0:
            total_start = dep_time
            layover_str = None
        else:
            # Only validate layover time if changing trains
            # If same train continues, no layover needed
            if current_train_number != prev_train_number:
                if prev_arrival_time:
                    layover = (dep_time - prev_arrival_time).total_seconds() / 60
                    
                    if layover < min_layover_min or layover > max_layover_min:
                        return None
                    
                    layover_str = f"{int(layover // 60)}h {int(layover % 60)}m"
                else:
                    layover_str = None
            else:
                # Same train continuing - no layover
                layover_str = "Same train (no transfer)"
        
        leg_info = {
            "leg_number": i + 1,
            "train_number": train["train_number"],
            "train_name": train["train_name"],
            "from_station": train["from_station"],
            "to_station": train["to_station"],
            "departure_time": _format_timestamp(dep_timestamp),
            "arrival_time": _format_timestamp(arr_timestamp),
        }
        
        if i > 0 and layover_str:
            leg_info["layover_before_this_leg"] = layover_str
        
        legs.append(leg_info)
        prev_arrival_time = arr_time
        prev_train_number = current_train_number
    
    # Calculate total journey time
    if total_start and prev_arrival_time:
        total_duration = prev_arrival_time - total_start
        hrs = int(total_duration.total_seconds() // 3600)
        mins = int((total_duration.total_seconds() % 3600) // 60)
        
        return {
            "total_hops": len(path),
            "total_journey_time": f"{hrs}h {mins}m",
            "intermediate_stations": [p[1] for p in path[:-1]],
            "legs": legs
        }
    
    return None


def _format_timestamp(timestamp: Optional[int]) -> str:
    """Convert epoch timestamp to readable format"""
    if timestamp is None:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


# Example usage
if __name__ == "__main__":
    # Test the functions
    journey_date = "2025-12-25"
    
    # Build graph
    print("Building graph...")
    graph = build_train_graph(journey_date, max_trains=20000)
    print(f"Graph has {len(graph)} edges")
    #print(graph)
    while True:
        from_station = input("Enter from station: ")
        to_station = input("Enter to station: ")
        max_hops = int(input("Enter max hops: "))
    
        # Find routes
        print("\nFinding routes...")
        routes = find_routes(from_station, to_station, journey_date, max_hops=max_hops, graph=graph)
        print(f"Found {routes['summary']['total_routes']} total routes")
        print(f"  - Direct: {routes['direct_routes']}")
        print(f"  - Multi-hop: {routes['multi_hop_routes']}")
