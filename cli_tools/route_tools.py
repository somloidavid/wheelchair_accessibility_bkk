from src.api_client import plan_trip
import os
from src.gtfs_tools import build_gtfs_network
import textwrap

U = '\033[4m'
R = '\033[0m'
B = '\033[1m'
I = '\033[3m'

ROUTE_TYPE_MAP = {
    0: "Tram",            # Standard Tram
    1: "Subway/Metro",    # M1, M2, M3, M4
    3: "Bus",             # Standard Blue Bus
    4: "Ferry",           # BKK Boat services
    11: "Trolleybus",     # Red Trolleybuses
    109: "HÉV", # HÉV (H5, H8, etc.)
    900: "Tram",          # Sometimes used for specific tram variants
}

window_size = os.get_terminal_size().columns
if not window_size:
    window_size = 80

def route_accessibility(network, linked_stops):
    print('|')
    print((f'{textwrap.fill('Route accessibility is a tool to help users gather information on the lines and stops themselves, not from an analytical, but a more user-friendly point of view.', width = window_size - 3, initial_indent='| ', subsequent_indent='| ' )}'))
    print('| ')
    