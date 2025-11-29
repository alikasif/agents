
import requests
from typing import Dict, List, Tuple, Optional, Set, Union
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



def _format_timestamp(timestamp: Optional[int]) -> str:
    """Convert epoch timestamp to readable format"""
    if timestamp is None:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def format_timestampv2(timestamp: int) -> str:
    
    # this function ensures that the timestamp is a valid tim ein HHMM format. for example 1630 is a valid time. but 495 is not a valid time.
    # basically 495 must be first converted into 0495 and then last 2 are extracted to get valid minutes. if it is greater then 60 then substract 60 from it and add 1 to hours.
    # pad 3 digits with 0
    timestamp = str(timestamp).zfill(4)
    
    hours = int(timestamp[:2])
    minutes = int(timestamp[2:])

    if minutes >= 60:
        hours += 1
        minutes -= 60
    return f"{hours:02d}{minutes:02d}"   


def convert_time_to_minutes(time_val: Union[str, int]) -> int:
    """
    Convert time in 'HHMM' format (e.g., '1300' or 1300) to total minutes from midnight.
    
    Args:
        time_val: Time string or integer (e.g., "1300", 1300)
    
    Returns:
        Total minutes from midnight (e.g., 13*60 + 0 = 780)
    """
    if isinstance(time_val, int):
        time_str = str(time_val)
    else:
        time_str = time_val
        
    # Remove any non-digit characters just in case
    time_str = ''.join(filter(str.isdigit, time_str))
    
    # Pad with leading zeros if needed (e.g., "500" -> "0500")
    time_str = time_str.zfill(4)
    
    if len(time_str) != 4:
        raise ValueError(f"Invalid time format: {time_val}")
        
    hours = int(time_str[:2])
    minutes = int(time_str[2:])
    
    return hours * 60 + minutes


def print_itinerary_table(route: Dict):
    """
    Print the itinerary in a tabular format.
    """
    print(f"\n{'='*100}")
    print(f"Total Hops: {route['total_hops']} | Total Journey Time: {route['total_journey_time']} | Intermediate Stations: {', '.join(route['intermediate_stations'])}")
    print(f"{'='*100}")
    
    # Header
    header = f"{'Leg':<5} | {'Train No':<8} | {'Train Name':<25} | {'From':<5} | {'To':<5} | {'Dep':<6} | {'Arr':<6} | {'Layover':<15}"
    print(header)
    print("-" * 100)
    
    for leg in route['legs']:
        # Format times
        dep_min = leg['departure_time']
        arr_min = leg['arrival_time']
        
        dep_str = dep_min  #f"{dep_min // 60:02d}:{dep_min % 60:02d}"
        arr_str =  arr_min #f"{arr_min // 60:02d}:{arr_min % 60:02d}"
        
        layover = leg.get('layover_before_this_leg', '-')
        
        row = f"{leg['leg_number']:<5} | {leg['train_number']:<8} | {leg['train_name'][:25]:<25} | {leg['from_station']:<5} | {leg['to_station']:<5} | {dep_str:<6} | {arr_str:<6} | {layover:<15}"
        
        print(row)
    print(f"{'='*100}\n")


def print_direct_trains(route):
    wrapped_route = {
                 'total_hops': 0,
                 'total_journey_time': route['total_journey_time'],
                 'intermediate_stations': [],
                 'legs': [{
                     'leg_number': 1,
                     'train_number': route['train_number'],
                     'train_name': route['train_name'],
                     'from_station': route['from_station'],
                     'to_station': route['to_station'],
                     'departure_time': route['departure_time'],
                     'arrival_time': route['arrival_time']
                 }]
             }
    print_itinerary_table(wrapped_route)


def calculate_total_journey_time(arrival_time: str, departure_time: str) -> str:
    

    arrival_time = convert_time_to_minutes(arrival_time)
    departure_time = convert_time_to_minutes(departure_time)
    total_duration = arrival_time - departure_time
    hrs = int(total_duration // 60)
    mins = int(total_duration % 60)
    return f"{hrs}h {mins}m"