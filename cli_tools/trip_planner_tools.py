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

def print_trip_plan(network):
    print('| ')
    print('| 1. QUICK TRIP PLANNER (Full Route Comparison)')
    print('| Enter coordinates like: 47.497,19.050')
    
    start = input('| START POINT: ').strip()
    end = input('| END POINT:   ').strip()
    
    if not start or not end:
        print('| [!] Error: Locations cannot be empty.')
        return

    print('| ' + '-' * 40)
    print('| Analyzing live network data...')

    try:
        endpoint = "otp/api/where/plan-trip"
        
        # get both versions
        opt_res = fetch_json(endpoint, params={"fromPlace": start, "toPlace": end, "mode": "TRANSIT,WALK", "wheelchair": "false"})
        acc_res = fetch_json(endpoint, params={"fromPlace": start, "toPlace": end, "mode": "TRANSIT,WALK", "wheelchair": "true"})

        def get_full_route_details(res):
            try:
                itinerary = res['data']['entry']['plan']['itineraries'][0]
                duration = itinerary['duration'] // 60
                route_steps = []
                
                for leg in itinerary.get('legs', []):
                    if leg.get('mode') != 'WALK':
                        line = leg.get('routeShortName', '???')
                        from_name = leg.get('from', {}).get('name', 'Start')
                        route_steps.append(f"Board [{line}] at {from_name}")
                        for stop in leg.get('intermediateStops', []):
                            route_steps.append(f"  ... {stop.get('name')}")
                        to_name = leg.get('to', {}).get('name', 'End')
                        route_steps.append(f"Exit [{line}] at {to_name}")
                
                return duration, route_steps
            except (KeyError, TypeError, IndexError):
                return None, []

        opt_time, opt_route = get_full_route_details(opt_res)
        acc_time, acc_route = get_full_route_details(acc_res)

        if opt_time is None:
            print('| [!] No route found.')
            return

        # check if the routes are same
        if opt_route == acc_route:
            print(f'| THE FASTEST ROUTE ({opt_time} min):')
            print('| (This route is fully wheelchair accessible)')
            for step in opt_route:
                print(f'|   {step}')
        else:
            print(f'| OPTIMAL ROUTE ({opt_time} min):')
            for step in opt_route:
                print(f'|   {step}')
            
            print('|' + '-' * 20)
            
            if acc_time is None:
                print('| ACCESSIBLE ROUTE: No path found!')
            else:
                print(f'| ACCESSIBLE ROUTE ({acc_time} min):')
                for step in acc_route:
                    print(f'|   {step}')
                
                print('|' + '-' * 20)
                diff = acc_time - opt_time
                print(f'| ANALYSIS: The accessible path takes {diff} min longer.')

    except Exception as e:
        print(f'| [!] Error: {e}')
    
    print('| ' + '-' * 40)


#ez a gyors utvonal ami neked kell de nekem nem pont igy kellett ugyhogy különszedtem 
#hogy igy értsd is hogy mi van mert az enyém az egy összevissza valami amit sztem csak én értek jelenleg
#hogy ertsd az egész gyakorlatilag az APIt használja de azt a funkciot konkrétan ami az útvonalat csinálja
#ez a fetch jsonos cucc ami egy ilyen listában a listában a lista cuccot ad vissza ezért van az itinerary már a try részben
#a leg-es rész kiszedi a visszaadott mátrix cuccbol az összes megállót és ennyi
#ha az is_accessible True akkor nyilvan csak accessible utat néz
def get_shortest_path_data(start_coords, end_coords, is_accessible=False):
    endpoint = "otp/api/where/plan-trip"
    res = fetch_json(endpoint, params={
        "fromPlace": start_coords,
        "toPlace": end_coords,
        "mode": "TRANSIT,WALK",
        "wheelchair": "true" if is_accessible else "false"
    })

    try:
        itinerary = res['data']['entry']['plan']['itineraries'][0]
        duration = itinerary['duration'] // 60
        stops = []
        
        for leg in itinerary.get('legs', []):
            if leg.get('mode') != 'WALK':
                line = leg.get('routeShortName', '???')
                from_stop = leg.get('from', {}).get('name', 'Start')
                to_stop = leg.get('to', {}).get('name', 'End')
                
                leg_stops = [from_stop]
                for s in leg.get('intermediateStops', []):
                    leg_stops.append(s.get('name'))
                leg_stops.append(to_stop)
                
                stops.append({"line": line, "path": leg_stops})
                
        return duration, stops
    except:
        return None, []
