try:
    from src.api_client import plan_trip, fetch_json
except ImportError:
    from api_client import plan_trip, fetch_json
import os
from src.gtfs_tools import build_gtfs_network
import textwrap
from cli_tools.network_tools import calculate_line_score
from collections import deque

U = '\033[4m'
R = '\033[0m'
B = '\033[1m'
I = '\033[3m'
G = '\033[92m'
GRAY = '\033[90m'

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

#1. print a whole line and show which stations are accessible
#2. maximum reach and maximum reach comparision
#3. islands of accessibility
#4. backtracking to inaccessible stations

def explore_route(network, linked_stops):
    graph = build_adjacency_graph(network)
    print('|')
    print((f'{textwrap.fill('Route accessibility is meant to be an explorational tool to help users gather information about the lines and stops themselves, especially from points of interest that fall outside the scope of everyday trips.', width = window_size - 3, initial_indent='| ', subsequent_indent='| ' )}'))
    try:
        while True:
            print('|')
            print(f'| {U}Options:{R}')
            print(f"| [1] Inspect a line and its stops")
            print(f"| [2] Maximum reach from a given stop and comparision")
            print(f'| [3] Find accessible islands in the network')
            print(f'| [4] Find inaccessible islands in the network')
            print(f'| [0] Return to the main menu')
            sub_choice = input('| -- PLEASE SELECT AN OPTION: ')
            print('|')
            if sub_choice.isdigit():
                sub_choice = int(sub_choice)
            else:
                print(f'| {I}Not a valid option{R}')
                continue
            if sub_choice == 1:
                print(f'| {I}[3.1 Inspecting a line]{R}')
                line_audit(network)
            elif sub_choice == 2:
                print(f"| {I}[3.2 Finding the maximum reach]{R}")
                max_reach(graph)
            elif sub_choice == 3:
                print(f'| {I}[3.3 Finding accessible islands]{R}')
                find_accessible_islands(graph)
            elif sub_choice == 4:
                print(f'| {I}[3.4 Finding inaccessible isalnds]{R}')
                find_inaccessible_islands(graph)
            elif sub_choice == 0:
                print(f"| {I}Returning to the main menu...{R}")
                break
    except Exception as e:
        print(f"[!] Analysis Error: {e}")
    print()
    print('-' * window_size)

#1 Line Audit
def line_audit(network):
     while True: 
         print(f"| {I}Type 'exit' to go back{R}")
         print('| ')
         line_name = input('| PLEASE ENTER THE NAME OF THE LINE (e.g. M4, 100E): ').upper().strip()
         if line_name == 'EXIT':
             print(f'| {I}Returning to network statistics menu...{R}')
             print('|')
             break
         all_matching_lines = [line for line in network.routes.values() if line.short_name == line_name]
         if not all_matching_lines:
             print(f'| [?] No matching lines found')
             continue
         matching_line = all_matching_lines[0]
         seen_stops = set()
         turnaround_idx = len(matching_line.stops)
         for idx, stop in enumerate(matching_line.stops):
             if stop.name in seen_stops:
                 turnaround_idx = idx
                 break
             seen_stops.add(stop.name)
         dir_1_stops = matching_line.stops[:turnaround_idx]
         dir_2_stops = matching_line.stops[turnaround_idx:]
         directions = {}
         if dir_1_stops:
             directions[dir_1_stops[-1].name] = dir_1_stops
         if dir_2_stops:
             directions[dir_2_stops[-1].name] = dir_2_stops
         headers = list(directions.keys())
         if not headers:
             print(f'| [?] No stops found for this line.')
             continue
         print(f'| ')
         print(f'| Available directions for {matching_line.short_name}:')
         for index, header in enumerate(headers):
             print(f'|  • [{index}] towards {header}')
         try:
             choice = int(input('| -- PLEASE SELECT AN OPTION: '))
             selected_line = directions[headers[choice]]
         except (ValueError, IndexError):
             print(f'| [!] Invalid selection')
             continue
         print('| ')     
         print(f'| {U}Line overview for {matching_line.short_name} towards {headers[choice]}:{R}')
         i = 0
         n = len(selected_line)
         max_streak = []
         current_streak = []
         for stop in selected_line:
             i += 1
             status = 'Accessible' if stop.wheelchair_boarding == 1 else 'Not Accessible'
             if status == 'Accessible':
                 current_streak.append(stop.name)
                 if n != i:
                    print(f'| {G}[{i}] {R}{stop.name:<10} | {status}')
                    print(f'| {G}|{R}')
                 elif n == i:
                     print(f'| {G}[{i}] {R}{stop.name:<10} | {status}')
                     print(f'|')
             elif status == 'Not Accessible':
                 if len(current_streak) > len(max_streak):
                     max_streak = current_streak
                 current_streak = []
                 if n != i:
                    print(f'| {GRAY}[{i}] {R}{stop.name:<10} | {status}')
                    print(f'| {GRAY}|{R}')
                 elif  i == n:
                     print(f'| {GRAY}[{i}] {R}{stop.name:<10} | {status}')
                     print('|')
         score = calculate_line_score(matching_line)
         if len(current_streak) > len(max_streak):
             max_streak = current_streak
         print(f'| OVERALL SCORE: {score:.0f}% accessible')
         if len(max_streak) > 1:
            print(f'| Longest consecutive stretch: {len(max_streak)} stops (from {max_streak[0]} to {max_streak[-1]}) ')
         else:
             print(f'| No consecutive accessible stops were found')
         print(f'| --------------------')
         print(f'| ')

#2 Find max reach
def max_reach(graph):
    while True:
        print(f'|')
        print(f"| {I} Type 'exit' or 0 to exit {R}")
        print(f'|')
        stop_name = input('| -- PLEASE ENTER THE NAME OF THE STATION: ').lower().strip()
        if stop_name == '0' or stop_name == 'exit':
            print(f'| {I}Returning to Explorer menu... {R}')
            print('|')
            break
        print(f'| {I}Mapping routes, please wait...{R}')
        print('| ')
        matches = [name for name in graph.keys() if stop_name in name.lower()]
        if not matches:
            print('| [?] No matching stops found')
            continue
        start_name = matches[0]
        accessible_count, accessible_furthest, accessible_distance = bfs(graph, start_name, is_accessible= True)
        total_count, total_furthest, total_distance = bfs(graph, start_name, is_accessible= False)
        print(f'| {U}Max distance reachable from {start_name}:{R}')
        if accessible_count == 0:
            print(f'| ACCESSIBLE REACH: 0 stops (Starting point is not accessible)')
        else:
            print(f'| • Accessible reach: {accessible_count} stops')
            print(f'|     -- Furthest point reachable: {accessible_furthest} ({accessible_distance} stops away)')
        print(f'| • Total reach: {total_count} stops')
        print(f'|     -- Furthest point reachable: {total_furthest} ({total_distance} stops away)')
        if total_count > 0:
            difference = (1- (accessible_count / total_count)) * 100
            print('|')
            print(f'| People in wheelchairs lose access to {difference:.1f}% of the network from {start_name}')

def build_adjacency_graph(network):
    graph = {}
    for line in network.routes.values():
        if hasattr(line, 'stops') and line.stops:
            for i in range(len(line.stops) - 1):
                 current = line.stops[i]
                 next_stop = line.stops[i + 1]
                 if current.name not in graph:
                     graph[current.name] = {}
                 if next_stop.name not in graph:
                     graph[next_stop.name] = {}
                 graph[current.name][next_stop.name] = next_stop
                 graph[next_stop.name][current.name] = current
    return graph

def bfs(graph, start_node_name, is_accessible = True):
    if start_node_name not in graph:
        return 0, 'Start is disconnected', 0
    starting_node = list(graph[start_node_name].values())[0] if graph[start_node_name] else None
    if starting_node and is_accessible and starting_node.wheelchair_boarding != 1:
        return 0, 'Start is inaccessible', 0
    visited = set([start_node_name])
    queue = deque([(start_node_name, 0)])
    max_distance = 0
    max_name = start_node_name
    while queue:
        current_name, distance = queue.popleft()
        if distance > max_distance:
            max_distance = distance
            max_name = current_name
        neighbours = graph.get(current_name, {})
        for neighbour_name, neighbour_obj in neighbours.items():
            if neighbour_name not in visited:
                if is_accessible and neighbour_obj.wheelchair_boarding != 1:
                    continue
                visited.add(neighbour_name)
                queue.append((neighbour_name, distance + 1))
    return len(visited), max_name, max_distance

#3 Find accessible islands
def find_accessible_islands(graph):
    print('| ')
    lone_islands = []
    for stop_name, neighbours in graph.items():
        if not neighbours:
            continue
        first_neighbour = list(neighbours.keys())[0]
        current_stop = graph[first_neighbour][stop_name]
        if current_stop.wheelchair_boarding == 1:
            continue
        is_surrounded = True
        for neighbor_name, neighbour_oject in neighbours.items():
            if neighbour_oject.wheelchair_boarding != 1:
                is_surrounded = False
                break
        if is_surrounded:
            lone_islands.append(stop_name)
    print('|')
    if not lone_islands:
        print(f'| In the Budapest transport network, there are no accessible stops that are completely surrounded by inaccessible stops ')
    else:
        print(f'| In the Budapest transport network there are {len(lone_islands)} accessible stops completely surrounded by inaccessible ones')
        print(f'|    This is about {len(lone_islands) / len(graph):.2f}% of all of the stops')
        for island in lone_islands[:10]:
            print(f'|    • {island} ')
        print('|    etc...')
    print("|")

#4 Find inaccessible islands
def find_inaccessible_islands(graph):
    print(f"|")
    lone_islands = []
    for stop_name, neighbours in graph.items():
        if not neighbours:
            continue
        first_neighbour = list(neighbours.keys())[0]
        current_stop = graph[first_neighbour][stop_name]
        if current_stop.wheelchair_boarding != 1:
            continue
        is_surrounded = True
        for neighbour_name, neighbour_object in neighbours.items():
            if neighbour_object.wheelchair_boarding == 1:
                is_surrounded = False
                break
        if is_surrounded:
            lone_islands.append(stop_name)
    print('|')
    if not lone_islands:
        print(f'| In the Budapest transport network, there are no accessible stops that are completely surrounded by inaccessible stops')
    else:
        print(f'| In the Budapest transport network there are {len(lone_islands)} accessible stops completely surrounded by inaccessible ones')
        print(f'|    This is about {len(lone_islands) / len(graph):.2f}% of all of the stops')
        for island in lone_islands[:10]:
            print(f'|    • {island} ')
        print(f'|    etc...')
    print(f'|')



                



        
