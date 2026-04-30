from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(slots=True)
class GTFSStop:
    id: str
    name: str | None
    lat: str | None
    lon: str | None
    wheelchair_boarding: bool | None
    lines: list[str] = field(default_factory=list)

@dataclass(slots=True)
class GTFSRoute:
    id: str
    short_name: str | None
    long_name: str | None
    route_type: int | None
    trip_count: int = 0
    accessible_trip_count: int = 0
    inaccessible_trip_count: int = 0
    unknown_trip_count: int = 0
    stop_count: int = 0
    accessible_stop_count: int = 0
    inaccessible_stop_count: int = 0
    unknown_stop_count: int = 0
    is_wheelchair_accessible: bool = False
    stops: list[GTFSStop] = field(default_factory=list)
    accessible_stops: list[GTFSStop] = field(default_factory=list)
    inaccessible_stops: list[GTFSStop] = field(default_factory=list)
    unknown_stops: list[GTFSStop] = field(default_factory=list)

@dataclass(slots=True)
class GTFSNetwork:
    routes: dict[str, GTFSRoute]
    stops: dict[str, GTFSStop]
    route_types: list[int]

    def accessible_routes(self) -> list[GTFSRoute]:
        return [route for route in self.routes.values() if route.is_wheelchair_accessible]

    def accessible_stops(self) -> list[GTFSStop]:
        return [stop for stop in self.stops.values() if stop.wheelchair_boarding is True]
