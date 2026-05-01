from gtfs_tools import build_gtfs_network
from models.gtfs import GTFSNetwork, GTFSStop, GTFSRoute

def extract_stops_from_response(gtfs_network: GTFSNetwork) -> dict[str, GTFSStop]:
	return gtfs_network.stops

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
		gtfs_network = build_gtfs_network()
		stops = extract_stops_from_response(gtfs_network)
		summary = count_accessible_stops(stops)
		accessible_routes = [route for route in gtfs_network.routes.values() if any(stop.wheelchair_boarding for stop in route.stops)]
		fully_accessible_routes = [route for route in gtfs_network.routes.values() if all(stop.wheelchair_boarding for stop in route.stops)]

		print(f"Routes in scope: {len(gtfs_network.routes)}")
		print(f"Wheelchair-accessible routes: {len(accessible_routes)}")
		print(f"Total stops in scope: {summary['total']}")
		print(f"Accessible stops: {summary['accessible']}")
		print(f"Inaccessible stops: {summary['inaccessible']}")
		print(f"Unknown stops: {summary['unknown']}")

		print("\nAccessible routes:")
		for route in accessible_routes[:10]:
			print(f"{GTFSRoute.ROUTE_TYPE_NAMES[route.route_type]} {route.short_name} ({route.id}): {len([stop for stop in route.stops if stop.wheelchair_boarding is True])} accessible stops")
		print("\nFully accessible routes:")
		for route in fully_accessible_routes[:10]:
			print(f"{GTFSRoute.ROUTE_TYPE_NAMES[route.route_type]} {route.short_name} ({route.id}): {len([stop for stop in route.stops if stop.wheelchair_boarding is True])} fully accessible stops")
		print("\nSample stops:")
		for stop_id, stop in list(stops.items())[:5]:
			print(f"  {stop.name} ({stop.id}): {stop.wheelchair_boarding}")
	except Exception as e:
		print(f"Error: {e}")
