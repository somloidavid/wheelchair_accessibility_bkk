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
        print('| 1. QUICK TRIP PLANNER (Optimal vs. Accessible)')
        print('| Note: Please enter coordinates in "lat,lon" format.')
        
        start = input('| START POINT: ').strip()
        end = input('| END POINT:   ').strip()
        
        if not start or not end:
            print('| [!] Error: Locations cannot be empty.')
            return
    
        print('| ' + '-' * 40)
        print('| Calculating and comparing routes...')
    
        try:
            
            endpoint = "otp/api/where/plan-trip"
            
            #Fetch Optimal Route
            opt_res = fetch_json(endpoint, params={
                "fromPlace": start,
                "toPlace": end,
                "mode": "TRANSIT,WALK",
                "wheelchair": "false"
            })
            
            #Fetch Accessible Route
            acc_res = fetch_json(endpoint, params={
                "fromPlace": start,
                "toPlace": end,
                "mode": "TRANSIT,WALK",
                "wheelchair": "true"
            })
    
            def get_time(res):
                try:
                    itineraries = res['data']['entry']['plan']['itineraries']
                    return itineraries[0]['duration'] // 60
                except (KeyError, TypeError, IndexError):
                    return None
    
            opt_time = get_time(opt_res)
            acc_time = get_time(acc_res)
    
            if opt_time is None:
                print('| [!] No route found. Check your coordinates (lat,lon).')
            else:
                print(f'| - Optimal Route:    {opt_time} minutes')
                if acc_time is None:
                    print('| - Accessible Route: No accessible path found!')
                else:
                    print(f'| - Accessible Route: {acc_time} minutes')
                    diff = acc_time - opt_time
                    if diff > 0:
                        print(f'| ANALYSIS: Accessibility adds {diff} minutes to the trip.')
                    else:
                        print('| ANALYSIS: The fastest route is wheelchair accessible!')
    
        except Exception as e:
            print(f'| [!] Error: {e}'))
