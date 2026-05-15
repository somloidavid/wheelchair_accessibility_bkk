from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass(slots=True)
class Location():
    name: str = ""
    stopId: Optional[str] = None

@dataclass(slots=True)
class Leg():
    to_loc: Location
    mode: str

@dataclass(slots=True)
class Itinerary():
    legs: List[Leg]

@dataclass(slots=True)
class Plan():
    itineraries: List[Itinerary]

@dataclass(slots=True)
class TripEntry():
    plan: Plan

@dataclass(slots=True)
class StopReference():
    wheelchairBoarding: bool

@dataclass(slots=True)
class References():
    stops: Dict[str, StopReference] = field(default_factory=dict)

@dataclass(slots=True)
class TripData():
    entry: TripEntry

@dataclass(slots=True)
class TripResponse():
    data: TripData
    currentTime: Optional[int] = None
    version: Optional[int] = None
    status: Optional[str] = None
    code: Optional[int] = None
    text: Optional[str] = None