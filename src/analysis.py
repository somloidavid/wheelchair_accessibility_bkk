def extract_stops_from_response(accessibility_index: dict) -> dict:
	return accessibility_index.get("stops", {})

def count_accessible_stops(stops: dict) -> dict:
    accessible = []
    inaccessible = []
    unknown = []
    
    for s in stops.values():
        status = s.get("wheelchair_boarding")
        
        if status is True:
            accessible.append(s)
        elif status is False:
            inaccessible.append(s)
        else:
            unknown.append(s)
    
    return {
		"total": len(stops),
		"accessible": len(accessible),
		"inaccessible": len(inaccessible),
		"unknown": len(unknown),
		"accessible_stops": accessible,
		"inaccessible_stops": inaccessible,
		"unknown_stops": unknown,
	}

if __name__ == "__main__":
	from gtfs_tools import build_accessibility_index, get_accessible_routes
	
	try:
		accessibility_index = build_accessibility_index()
		stops = extract_stops_from_response(accessibility_index)
		summary = count_accessible_stops(stops)
		accessible_routes = get_accessible_routes(accessibility_index)
		
		print(f"Routes in scope: {len(accessibility_index['routes'])}")
		print(f"Wheelchair-accessible routes: {len(accessible_routes)}")
		print(f"Total stops in scope: {summary['total']}")
		print(f"Accessible stops: {summary['accessible']}")
		print(f"Inaccessible stops: {summary['inaccessible']}")
		print(f"Unknown stops: {summary['unknown']}")
		
		print("\nAccessible routes:")
		for route in accessible_routes[:10]:
			print(f"  {route['short_name']} ({route['id']}): {route['accessible_stop_count']} accessible stops")
		print("\nSample stops:")
		for stop_id, stop in list(stops.items())[:5]:
			print(f"  {stop['name']} ({stop['id']}): {stop['wheelchair_boarding']}")
	except Exception as e:
		print(f"Error: {e}")
