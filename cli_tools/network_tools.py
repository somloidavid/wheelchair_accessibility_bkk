from src.api_client import plan_trip
import os
from src.gtfs_tools import build_gtfs_network

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

def network_statistics(network, linked_stops):
    print("| Loading data (this might take a moment)...")
    try:
        network_statistics_intro(network)
        while True:
            print('|')
            print(f'| {U}Network statistics further options:{R}')
            print(f"| [1] Find whether a stop is accessible")
            print(f"| [2] Find whether a line is accessible")
            print(f'| [3] List the most accessible stations')
            print(f'| [4] List means of transport by accessibility')
            print(f"| [5] Show accessibilty diagrams")
            print(f'| [0] Return to the main menu')
            sub_choice = input('| -- PLEASE SELECT AN OPTION: ')
            print('|')
            if sub_choice.isdigit():
                sub_choice = int(sub_choice)
            else:
                print(f'| {I}Not a valid option{R}')
                continue
            if sub_choice == 1:
                print(f'| {I}[2.1 Finding a stop]{R}')
                find_stop(network)
            elif sub_choice == 2:
                print(f"| {I}[2.2 Finding a line]{R}")
                find_line(network)
            elif sub_choice == 3:
                print(f'| {I}[2.3 Listing accessible stations]{R}')
            elif sub_choice == 4:
                print(f'| {I}[2.4 Listing accessible means of transport]{R}')
            elif sub_choice == 5:
                print(f'| {I}[2.5 Showing accessibility diagrams]{R}')
            elif sub_choice == 0:
                print(f"| {I}Returning to the main menu...{R}")
                break
    except Exception as e:
        print(f"[!] Analysis Error: {e}")
    print()
    print('-' * window_size)

def network_statistics_intro(network):
     total_stops = len(network.stops)
     accessible_stops = sum(1 for stop in network.stops.values() if stop.wheelchair_boarding)
     if total_stops > 0:
        percentage = (accessible_stops / total_stops) * 100
     else:
        percentage = 0
     print('|')
     print(f"| GENERAL RESULTS ABOUT THE BKK NETWORK")
     print(f"|  ● Total stops analyzed:    {total_stops}")
     print(f"|  ● Accessible stops:        {accessible_stops}")
     print(f"|  ● Overall Accessibility:   {percentage:.2f}%")

#1
def find_stop(network):
    while True:
        print(f"| {I}Type '0' or 'exit' to go back{R}")
        stop_name = input('| PLEASE ENTER THE NAME OF THE STOP: ').lower().strip()
        if stop_name in ('exit', '0'):
            print(f'| {I}Returning to network statistics menu...{R}')
            print('|')
            break
        stop_name_dict = {}
        for stop in network.stops.values():
            if stop_name in stop.name.lower() and stop.name not in stop_name_dict:
                stop_name_dict[stop.name] = stop
        if not stop_name_dict:
            print(f'| [?] There are no stops with a matching name')
            continue 
        print('|')
        print(f'| Matching stops found:')
        i = 0
        for name, stop in stop_name_dict.items():
            i += 1
            status = 'Accessible' if stop.wheelchair_boarding else 'Not Accessible'
            print(f'| {i}. {name:<20}: {status:<15}')
            if hasattr(stop, 'routes') and stop.routes:
                route_names = sorted({route.short_name for route in stop.routes})
                routes_string = ', '.join(route_names)
                print(f'|   Lines: {routes_string}')
            else:
                print(f'|    {I}No lines found for this stop{R}')
        print('|')
    print('|')

#2
def find_line(network):
    while True:
        print(f"| {I}Type 'exit' to go back{R}")
        line_name = input('| PLEASE ENTER THE NAME OF THE LINE (e.g. M4, 100E): ').upper().strip()
        if line_name in ('EXIT'):
            print(f'| {I}Returning to network statistics menu...{R}')
            print('|')
            break
        lines_found = [line for line in network.routes.values() if line_name == line.short_name.upper()]
        if not lines_found:
            print(f'| [?] No matching lines found')
            continue
        print('|')
        print(f'| Matching lines found:')
        i = 0
        for line in lines_found:
            i += 1
            line_type = ROUTE_TYPE_MAP.get(line.route_type, 'Vehicle')
            status = find_line_accessibilty(line)
            print(f'| {i}. {line.short_name} ({line_type})')
            print(f'|    {status}')
        print('|')

def find_line_accessibilty(line):
    if not line.stops:
        return "No stop data"
    total_stops = len(line.stops)
    accessible_count = sum(1 for stop in line.stops if stop.wheelchair_boarding == 1)
    percentage = (accessible_count / total_stops) * 100
    return f"{accessible_count}/{total_stops} stops are accessible ({percentage:.2f} %)"

#3
def list_top_accessible(network, linked_stops):
    pass




