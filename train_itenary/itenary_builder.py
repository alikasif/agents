import requests
from typing import Dict, List, Tuple, Optional, Set, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
import time
from utils import *
from datetime import date
from train_graph_builder import build_train_graph
from itertools import product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_TRAINS = 500

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
        logger.info("Building train graph")
        graph = build_train_graph(journey_date, max_trains=MAX_TRAINS)
    
    # Find all paths using BFS
    all_paths = _find_all_paths_bfs(graph, from_station, to_station, max_hops)
    #logger.info(f"Found {all_paths} possible paths")
    
    result = {
        "direct_routes": [],
        "multi_hop_routes": [],
        "summary": {}
    }
    
    # Process paths
    for path in all_paths:
        #logger.info(f"Processing path {path} of length {len(path)}")

        if len(path) == 1:
            # Direct route
            from_st, to_st = path[0]
            trains = graph.get((from_st, to_st), [])
            #logger.info(f"Found {trains} trains for direct route")

            for train in trains:
                total_duration = calculate_total_journey_time(train["arrival_time"], train["departure_time"])

                result["direct_routes"].append({
                    "train_number": train["train_number"],
                    "train_name": train["train_name"],
                    "from_station": from_st,
                    "to_station": to_st,
                    "departure_time": train["departure_time"],
                    "arrival_time": train["arrival_time"],
                    "total_journey_time": total_duration,
                    "from_day": train["from_day"],
                    "to_day": train["to_day"]
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
    
    # Get all train options for each leg
    leg_options = []
    for from_st, to_st in path:
        trains = graph.get((from_st, to_st), [])
        #logger.info(f"Found {trains} trains for leg {from_st} -> {to_st}")
        if not trains:
            return []
        leg_options.append(trains)
    
    valid_routes = []
    
    #logger.info(f"Found leg options \n\n {leg_options}\n\n")

    # Try all combinations of trains
    for train_combination in product(*leg_options):
        #logger.info(f"Processing train combination {train_combination}")
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
    start_day = None
    end_day = None

    for i, train in enumerate(trains):
        dep_timestamp = train["departure_time"]
        arr_timestamp = train["arrival_time"]
        current_train_number = train["train_number"]

        #logger.info(f"Processing train {current_train_number} from {train['from_station']} to {train['to_station']} with departure time {dep_timestamp} and arrival time {arr_timestamp}")
        
        if dep_timestamp is None or arr_timestamp is None:
            return None
        
        if current_train_number == prev_train_number:
            leg_info["to_station"] = train["to_station"]
            continue
        
        # Convert timestamps to datetime
        # dep_time = datetime.fromtimestamp(dep_timestamp)
        # arr_time = datetime.fromtimestamp(arr_timestamp)

        dep_time = dep_timestamp
        arr_time = arr_timestamp

        #logger.info(f"Departure time: {dep_time}, Arrival time: {arr_time}")
        
        # For first leg, record start time
        if i == 0:
            total_start = dep_time
            start_day = train["from_day"]
            layover_str = None
        else:
            # Only validate layover time if changing trains
            # If same train continues, no layover needed
            if current_train_number != prev_train_number:
                if prev_arrival_time:
                    
                    layover = convert_time_to_minutes(dep_time) - convert_time_to_minutes(prev_arrival_time)
                                        
                    if layover < min_layover_min or layover > max_layover_min:
                        #logger.info(f"Invalid layover time: {layover} minutes. departure time: {dep_time}, arrival time: {prev_arrival_time}")
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
            "departure_time": dep_timestamp,
            "arrival_time": arr_timestamp,
        }
        
        if i > 0 and layover_str:
            leg_info["layover_before_this_leg"] = layover_str
        
        legs.append(leg_info)
        prev_arrival_time = arr_time
        end_day = train["to_day"]
        prev_train_number = current_train_number
    

    # Calculate total journey time
    if total_start and prev_arrival_time:
        total_duration = calculate_total_journey_time(prev_arrival_time, total_start)
        
        return {
            "total_hops": len(path),
            "total_journey_time": total_duration,
            "intermediate_stations": [p[1] for p in path[:-1]],
            "legs": legs
        }
    
    return None



# Example usage
if __name__ == "__main__":
        
    journey_date = date.today().isoformat()
    start_time = time.time()
    graph = build_train_graph(journey_date, max_trains=500)
    end_time = time.time()
    
    logger.info(f"\n\nAll stations :: {graph.keys()}\n\n")

    logger.info(f"Graph built in {end_time - start_time} seconds\n\n")
    
    
    while True:
        from_station = input("Enter from station: ")
        to_station = input("Enter to station: ")
        max_hops = int(input("Enter max hops: "))
    
        # Find routes
        logger.info("\nFinding routes...")
        routes = find_routes(from_station, to_station, journey_date, max_hops=max_hops, graph=graph)

        #logger.info(f"\nFound {routes['summary']['total_routes']} total routes")

        print("\n--- Direct Routes ---")
        for route in routes['direct_routes']:             
            print_direct_trains(route)
             

        print("\n--- Multi-Hop Routes ---")
        for route in routes['multi_hop_routes']:
            print_itinerary_table(route)
