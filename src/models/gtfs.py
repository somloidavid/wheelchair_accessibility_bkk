from dataclasses import dataclass, field
from typing import ClassVar

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
    stops: list[GTFSStop] = field(default_factory=list)

    ROUTE_TYPE_NAMES: ClassVar[dict[int, str]] = {
        0: "Tram",
        1: "Metro",
        3: "Bus"
    }

@dataclass(slots=True)
class GTFSNetwork:
    routes: dict[str, GTFSRoute]
    stops: dict[str, GTFSStop]
    route_types: list[int]