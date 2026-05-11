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

#this is the 'main' under this branch
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
                find_stop(network, linked_stops)
            elif sub_choice == 2:
                print(f"| {I}[2.2 Finding a line]{R}")
                find_line(network)
            elif sub_choice == 3:
                print(f'| {I}[2.3 Listing accessible stations]{R}')
                list_top_accessible(network, linked_stops)
            elif sub_choice == 4:
                print(f'| {I}[2.4 Listing accessible means of transport]{R}')
                list_top_accessible_transport(network)
            elif sub_choice == 5:
                print(f'| {I}[2.5 Showing accessibility diagrams]{R}')
            elif sub_choice == 0:
                print(f"| {I}Returning to the main menu...{R}")
                break
    except Exception as e:
        print(f"[!] Analysis Error: {e}")
    print()
    print('-' * window_size)

#prints the intro 
def network_statistics_intro(network):
     total_stops = len(network.stops)
     accessible_stops = sum(1 for stop in network.stops.values() if stop.wheelchair_boarding)
     if total_stops > 0:
        percentage = (accessible_stops / total_stops) * 100
     else:
        percentage = 0
     print('|')
     print(f"| GENERAL RESULTS ABOUT THE BKK NETWORK")
     print(f"|  • Total stops analyzed:    {total_stops}")
     print(f"|  • Accessible stops:        {accessible_stops}")
     print(f"|  • Overall Accessibility:   {percentage:.2f}%")

#1
def find_stop(network, linked_stops):
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
            current_lines = linked_stops.get(name, set())
            if current_lines:
                lines_string = sorted({line for line in current_lines})
                print(f'|    -- Lines: {textwrap.fill(', '.join(lines_string), width = window_size - 5, initial_indent='| ', subsequent_indent= '| ')}')
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
     print('| ')
     while True:
         enter = input(f'| {I}The algorithm works with a 75% accessibility rate. Would you like to change it? (y/n){R}').lower()
         if enter == 'y':
             rate = int(input(f'| {I}--Please enter the new value (as an integer): {R}'))
             break
         elif enter == 'n':
             rate = 75
             break
         else:
             continue
     print('| ')
     while True:
         print(f'|')
         enter = input(f'| {I}The default return is 10 items, would you like to change it? (y/n){R}').lower()
         if enter == 'n':
             n = 10
             break
         elif enter == 'y':
             n = int(input(f' | {I}--Please enter the new value: {R}'))
             if n > 0:
                break
             else:
                 continue
         else:
             continue
     top_list = []
     for stop in network.stops.values():
         if stop.wheelchair_boarding == 1:
             lines = linked_stops.get(stop.name, set())
             total_stop_count = len(lines)
             acc_lines = []
             for line in lines:
                 route = next((r for r in network.routes.values() if r.short_name == line), None)
                 if route:
                     score = calculate_line_score(route)
                     if score > rate:
                         acc_lines.append(line)
             top_list.append((stop.name, total_stop_count, len(acc_lines), acc_lines))
     unique_list = []
     unique_check = set()
     for name, total_count, count, lines in sorted(top_list, key = lambda x: x[2], reverse = True):
         if name not in unique_check:
             unique_list.append((name, total_count, count, lines))
             unique_check.add(name)
     print('|')
     print(f'| Top {n} stops in Budapest ranked by accessibility')
     i = 0
     for name, total_count, count, lines in unique_list[:n]:
         i += 1
         percentage = (count / total_count * 100) if total_count > 0 else 0
         print(f'| {i}. {name:<25} | {count:<2} |  altogether {percentage:.2f}% accessible')
         print(f'|    -- Accessible lines: {textwrap.fill(', '.join(sorted(lines)), width = window_size - 2, initial_indent='| ', subsequent_indent= '| ')}')
     print('|')

def calculate_line_score(line):
    if not line.stops:
        return 0.0
    total_stops = len(line.stops)
    accessible_count = sum(1 for stop in line.stops if stop.wheelchair_boarding == 1)
    percentage = (accessible_count / total_stops) * 100
    return (accessible_count / total_stops) * 100

#4
def list_top_accessible_transport(network):
    print(f'|')
    print(f'| Top accessible means of transport in Budapest')
    transport_groups = {}
    for line in network.routes.values():
        line_type = line.route_type
        if line_type not in transport_groups:
            transport_groups[line_type] = []
        transport_groups[line_type].append(line)
    for line_type, lines in transport_groups.items():
        type_name = ROUTE_TYPE_MAP.get(line_type, f'Other ({line_type})')
        line_scores = []
        for l in lines:
            score = calculate_line_score(l)
            line_scores.append((l.short_name, score))
        avg_accessibility = sum(s for name, s in line_scores) / len(line_scores)
        top_3 = sorted(line_scores, key = lambda x: x[1], reverse = True)[:3]
        top_3_string = [f"{name} ({score})" for name, score in top_3]
        print(f'| ◦ {type_name.upper():<25} | altogether {avg_accessibility :.2f}% accessible')
        print(f"|    -- Top 3 most accessible lines: {', '.join(top_3_string)} ")
    print('|')