import requests
from typing import Dict, List, Tuple, Optional, Set, Union
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging
from multiprocessing import Pool
import time
from utils import format_timestampv2

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from utils import get_all_trains, get_train_data


def build_train_graph(journey_date: str, max_trains: int = 500):
    """
    Build a graph where stations are nodes and trains are edges.
    
    Args:
        journey_date: Journey date in YYYY-MM-DD format
        max_trains: Maximum number of trains to process (to limit API calls)
    
    Returns:
        Dictionary with (from_station, to_station) tuples as keys and list of trains as values
        Example: {("NDLS", "AGC"): [{train_number, train_name, departure_time, arrival_time, ...}]}
    """
    #logger.info(f"Building train graph for {journey_date} (processing up to {max_trains} trains)")
    
    # Get all trains
    all_trains_response = get_all_trains()
    if not all_trains_response.get("success") or not all_trains_response.get("data"):
        logger.error("Failed to fetch all trains")
        return {}
    
    all_trains = all_trains_response["data"][:max_trains]
    #logger.info(f"Processing {len(all_trains)} trains")
    
    prev = 0
    index = 0
    batch_size = 25
    results = []

    pool = Pool(processes=22)   
    while index < len(all_trains):
        graph = defaultdict(list)
        #logger.info(f"Processing {index} to {index + batch_size}")
        index += batch_size
        if index > len(all_trains):
            index = len(all_trains)
        
        trains = all_trains[prev:index]
        results.append(pool.apply_async(build_train_data_map_v2, args=(graph, journey_date, trains)))
        prev = index
        
    pool.close()
    pool.join()
    
    main_graph = defaultdict(list)
    for result in results:
        main_graph.update(result.get())

        # logger.info(f"Processing result {len(result.get())}")   
        # for k,v in result.get().items():
        #     if main_graph.get(k):
        #         #logger.info(f"Duplicate key {k}")
        #         main_graph[k].extend(v)
        #     else:
        #         main_graph[k] = v
    
    #logger.info(f"Graph built with {len(main_graph)} unique station pairs from trains")
    return main_graph


def build_train_data_map_v2(graph: Dict[Tuple[str, str], List[Dict]], journey_date: str, all_trains: List[Tuple[str, str]]) -> Dict[Tuple[str, str], List[Dict]]:

    #logger.info(f"Processing {len(all_trains)} train graph {len(graph)}")
    processed = 0
    edges =0

    for train_entry in all_trains:
        train_number = train_entry[0]
        train_name = train_entry[1]
        
        try:
            # Get detailed route data for this train
            train_data = get_train_data(train_number, journey_date)
            
            if not train_data.get("data") or not train_data["data"].get("route"):
                continue
            
            route = train_data["data"]["route"]
            
            # create a map of station to route
            station_to_index = {stop["stationCode"]: stop for stop in route}

            # extract all the stations in the route where isHalt == 1
            stations = [stop["stationCode"] for stop in route if stop["isHalt"] == 1]
            #logger.info(f"train {train_number} pass through {len(stations)} stations")

            # now create a edge between every station
            for i in range(len(stations) - 1):
                from_station = stations[i]
                from_stop = station_to_index[from_station]
                to_station = stations[i + 1]
                to_stop = station_to_index[to_station]
                                
                if not from_station or not to_station:
                    #logger.info(f"No stations found for train {train_number} edge {from_station} -> {to_station}")
                    continue
                
                #logger.info(f"train {train_number} edge {from_station} -> {to_station}")
                
                # Create edge with train information
                edge = {
                    "train_number": train_number,
                    "train_name": train_name,
                    "from_station": from_station,
                    "from_station_name": from_stop.get("stationName"),
                    "to_station": to_station,
                    "to_station_name": to_stop.get("stationName"),
                    "departure_time": format_timestampv2(from_stop.get("scheduledDeparture")),  # epoch timestamp or None
                    "arrival_time": format_timestampv2(to_stop.get("scheduledArrival")),  # epoch timestamp or None
                    # "distance_km": to_stop.get("distanceFromSourceKm", 0) - from_stop.get("distanceFromSourceKm", 0),
                    "from_day": from_stop.get("day", 1),
                    "to_day": to_stop.get("day", 1),
                    # "running_days_bitmap": train_info.get("runningDaysBitmap"),
                }
                edges+=1
                
                graph[(from_station, to_station)].append(edge)
                #logger.info(f"Added edge {from_station} -> {to_station} with train {train_number} arrival time: {to_stop.get('scheduledArrival')} departure time: {from_stop.get('scheduledDeparture')}")
            
            processed += 1
            if processed % 50 == 0:
                logger.info(f"Processed {processed}/{len(all_trains)} trains")
                
        except Exception as e:
            logger.debug(f"Error processing train {train_number}: {e}")
            continue
    
    logger.info(f"Graph built with {len(graph)} unique station pairs from {processed} trains edges {edges}")
    return dict(graph)
            


if __name__ == "__main__":
    start_time = time.time()
    graph = build_train_graph("2025-11-29", max_trains=2000)
    end_time = time.time()
    logger.info(f"Graph built with {len(graph)} unique station pairs from trains")
    logger.info(f"Time taken: {end_time - start_time} seconds")