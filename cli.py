import sys
from src.api_client import plan_trip
import textwrap
import os
from src.gtfs_tools import build_gtfs_network
from cli_tools.network_tools import network_statistics
from cli_tools.route_tools import route_accessibility
from cli_tools.trip_planner_tools import print_trip_plan

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
    109: "HÉV",           # HÉV (H5, H8, etc.)
    900: "Tram",          # Sometimes used for specific tram variants
}

#prints the intro
def print_intro():
    print('=' * window_size)
    print()
    print(f"      --- {B}BKK WHEELCHAIR ACCESSIBILITY{R} ---".center(window_size))
    print('Advanced Programming project by Group 2:'.center(window_size))
    print('Péter Galambos, Csenge Lendvai, Jiahui Ren, Dávid Somlói'.center(window_size))
    print()
    print(f'-- {B}Project description:{R}')
    print()
    introduction_text = 'Our main goal with this project was to gather data from the BKK and analyze tram, bus and metro routes from the point of view of wheelchair accessibility. Specifically, to determine the share of the network that is accessible by wheelchair, so naturally, one of our aims was to generate a list of accessible stations from a given startpoint. For this, we had to use the BKK API, clean and analyze the data, then present it in an understandable and clean format. For this, we opted to use a menu resembling a CLI application and some graphs we created from scratch.'
    print(textwrap.fill(introduction_text, width = (window_size - 2), initial_indent=' '))
    print()
    print(f' -- {U}Some key questions from our project:{R} ')
    print(f"  ●  How many stops can you reach from a given station?")
    print(f"  ●  Are there any 'isolated' areas (inaccessible by wheelchairs)? ")
    print(f"  ●  Is the shortest route entirely accessible?")
    print()

#prints the main menu, returns the choice as an integer
def print_menu():
    print(f' -- {B}MAIN MENU{R} --')
    print('[1] Quick trip planner (Optimal vs. Accessible)')
    print('[x] Plan an accessible trip') # i will do it tomorrow
    print('[2] Network accessibility statistics')
    print('[3] Explore the transport network of Budapest')
    print('[0] Exit program')
    choice = int(input(' -- PLEASE SELECT AN OPTION: '))
    return choice
    
#runs the whole thing
def run_cli():
    global window_size
    window_size = os.get_terminal_size().columns
    if not window_size:
        window_size = 80
    print(f"{I}Loading network data (please wait)...{R}")
    network = build_gtfs_network()
    linked_stops = create_stop_to_route_map(network)
    print()
    print_intro()
    print('-' * window_size)
    print()
    while True:
        choice = print_menu()
        print()
        if choice == 1:
            print(f'{B}1. Planning an accessible trip{R}')
            print_trip_plan(network)
        elif choice == 2:
            print(f'{B}2. Showing network accessbility statistics{R}')
            network_statistics(network, linked_stops)
        elif choice == 3:
            print(f'{B}3. Showing line accessibily details{R}')
            route_accessibility(network, linked_stops)
        elif choice == 0:
            print(f'{I}Exiting program...{R}')
            print('='* window_size)
            break
        else:
            print(f'{I}Not a valid option{R}')
            pass
        print()


#i use this to map routes/lines to stops
def create_stop_to_route_map(network):
    stop_map = {}
    for route in network.routes.values():
        if hasattr(route, 'stops') and route.stops:
            for stop in route.stops:
                if stop.name not in stop_map:
                    stop_map[stop.name] = set()
                stop_map[stop.name].add(route.short_name)
    return stop_map


run_cli()

