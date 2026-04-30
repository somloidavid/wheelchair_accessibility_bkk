from gtfs_tools import build_accessibility_index, get_accessible_routes
from models.gtfs import GTFSNetwork, GTFSStop

def extract_stops_from_response(accessibility_index: GTFSNetwork) -> dict[str, GTFSStop]:
	return accessibility_index.stops

def count_accessible_stops(stops: dict[str, GTFSStop]) -> dict:
	accessible = []
	inaccessible = []
	unknown = []

	for stop in stops.values():
		status = stop.wheelchair_boarding

		if status is True:
			accessible.append(stop)
		elif status is False:
			inaccessible.append(stop)
		else:
			unknown.append(stop)

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
	try:
		accessibility_index = build_accessibility_index()
		stops = extract_stops_from_response(accessibility_index)
		summary = count_accessible_stops(stops)
		accessible_routes = get_accessible_routes(accessibility_index)

		print(f"Routes in scope: {len(accessibility_index.routes)}")
		print(f"Wheelchair-accessible routes: {len(accessible_routes)}")
		print(f"Total stops in scope: {summary['total']}")
		print(f"Accessible stops: {summary['accessible']}")
		print(f"Inaccessible stops: {summary['inaccessible']}")
		print(f"Unknown stops: {summary['unknown']}")

		print("\nAccessible routes:")
		for route in accessible_routes[:10]:
			print(f"  {route.short_name} ({route.id}): {route.accessible_stop_count} accessible stops")
		print("\nSample stops:")
		for stop_id, stop in list(stops.items())[:5]:
			print(f"  {stop.name} ({stop.id}): {stop.wheelchair_boarding}")
	except Exception as e:
		print(f"Error: {e}")
