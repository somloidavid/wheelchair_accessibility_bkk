from src.api_client import fetch_json
from src.gtfs_tools import build_gtfs_network, extract_stops_from_response, count_accessible_stops, get_accessible_routes

# url = "https://futar.bkk.hu/api/query/v1/ws"
# data = fetch_json(url)
# print(data[:5])

network = build_gtfs_network()