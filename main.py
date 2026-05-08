from src.gtfs_tools import build_gtfs_network
from src.api_client import plan_trip

# network = build_gtfs_network()
#Örs vezér tere M+H:47.503260,19.137956
#Bécsi út / Vörösvári út:47.546762,19.029194
trip = plan_trip("47.503260,19.137956", "47.546762,19.029194", ["TRAM", "SUBWAY", "WALK"], True).data

itineraries = trip.get("entry", {}).get("plan", {}).get("itineraries", [])

unique_routes = set()
n = 1
for itinerary in itineraries:
    transit_legs = [
        f"{leg.get('routeShortName', leg.get('mode'))} (from {leg.get('from', {}).get('name')} to {leg.get('to', {}).get('name')})"
        for leg in itinerary.get("legs", []) 
        if leg.get("mode") != "WALK"
    ]
    
    route_signature = " -> ".join(transit_legs)
    if route_signature and route_signature not in unique_routes:
        unique_routes.add(route_signature)
        print(f"Option {n}: {route_signature}")
        n += 1