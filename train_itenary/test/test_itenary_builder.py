from train_itenary.itenary_builder import find_routes

def get_dummy_graph():
    return {
        ("NDLS", "AGC"): [{"train_number": "12345", "train_name": "Express1", "departure_time": 1300, "arrival_time": 1700, "from_station": "NDLS", "to_station": "AGC"}],
        ("AGC", "KTH"): [{"train_number": "54321", "train_name": "Express2", "departure_time": 1900, "arrival_time": 2200, "from_station": "AGC", "to_station": "KTH"}],
        ("NDLS", "KTH"): [{"train_number": "56214", "train_name": "Express3", "departure_time": 1100, "arrival_time": 2300, "from_station": "NDLS", "to_station": "KTH"}],

        ("A", "B"): [{"train_number": "112233", "train_name": "Express11", "departure_time": 900, "arrival_time": 1200, "from_station": "A", "to_station": "B"}],
        ("B", "C"): [{"train_number": "11334", "train_name": "Express12", "departure_time": 1300, "arrival_time": 1500, "from_station": "B", "to_station": "C"}],
        ("C", "D"): [{"train_number": "11445", "train_name": "Express13", "departure_time": 1600, "arrival_time": 1800, "from_station": "C", "to_station": "D"}],
        ("A", "C"): [{"train_number": "11556", "train_name": "Express14", "departure_time": 1100, "arrival_time": 1900, "from_station": "A", "to_station": "C"}],
        ("B", "D"): [{"train_number": "11667", "train_name": "Express15", "departure_time": 1230, "arrival_time": 1830, "from_station": "B", "to_station": "D"}],
        ("C", "E"): [{"train_number": "11778", "train_name": "Express16", "departure_time": 1800, "arrival_time": 2300, "from_station": "C", "to_station": "E"}],

    }

journey_date = "2025-12-25"

# Build graph
print("Building graph...")
#graph = build_train_graph(journey_date, max_trains=500)
graph = get_dummy_graph()
print(f"Graph has {len(graph)} edges")
routes = find_routes("A", "D", journey_date, max_hops=5, graph=graph)

print(f"Found {routes['summary']['total_routes']} total routes")
print(f"  - Direct: {routes['direct_routes']}")
print(f"  - Multi-hop: {routes['multi_hop_routes']}")
