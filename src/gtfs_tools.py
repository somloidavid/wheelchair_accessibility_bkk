import csv
import os
import shutil
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Sequence
from urllib.request import Request, urlopen
from zipfile import ZipFile
try:
    from src.models.gtfs import GTFSNetwork, GTFSRoute, GTFSStop
except ImportError:
    from models.gtfs import GTFSNetwork, GTFSRoute, GTFSStop

GTFS_ZIP_URL = os.getenv(
    "GTFS_ZIP_URL",
    "https://go.bkk.hu/api/static/v1/public-gtfs/budapest_gtfs.zip",
)
GTFS_DATA_DIR = Path(os.getenv("GTFS_DATA_DIR", "data"))
GTFS_EXTRACT_DIR = Path(os.getenv("GTFS_EXTRACT_DIR", f"{GTFS_DATA_DIR}/budapest_gtfs"))

gtfs_path = os.getenv("DEFAULT_GTFS_PATH", str(GTFS_EXTRACT_DIR))

TRAM_ROUTE_TYPE = 0
METRO_ROUTE_TYPE = 1
BUS_ROUTE_TYPE = 3
DEFAULT_ROUTE_TYPES = (TRAM_ROUTE_TYPE, METRO_ROUTE_TYPE, BUS_ROUTE_TYPE)

REQUIRED_GTFS_FILES = (
    "routes.txt",
    "stops.txt",
    "trips.txt",
    "stop_times.txt",
)

def _download_gtfs_zip(zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    request = Request(GTFS_ZIP_URL, headers={"Accept": "application/zip"})
    with urlopen(request) as response, open(zip_path, "wb") as target_file:
        shutil.copyfileobj(response, target_file)

def _extract_gtfs_zip(zip_path: Path, extract_dir: Path) -> Path:
    if extract_dir.exists():
        shutil.rmtree(extract_dir)

    extract_dir.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=extract_dir.parent) as temp_dir:
        temp_extract_dir = Path(temp_dir) / "extract"
        temp_extract_dir.mkdir(parents=True, exist_ok=True)
        with ZipFile(zip_path) as archive:
            archive.extractall(temp_extract_dir)

        shutil.copytree(temp_extract_dir, extract_dir)

    return extract_dir

def ensure_gtfs_root(candidate_path: str | os.PathLike[str] | None = None) -> str:
    candidate = Path(candidate_path) if candidate_path else None

    if candidate is not None:
        if candidate.is_file() and candidate.suffix.lower() == ".zip":
            extracted = _extract_gtfs_zip(candidate, GTFS_EXTRACT_DIR)
            return str(extracted)

        if candidate.exists() and candidate.is_dir():
            return str(candidate)

    if GTFS_EXTRACT_DIR.exists():
        return str(GTFS_EXTRACT_DIR)

    zip_path = GTFS_DATA_DIR / "budapest_gtfs.zip"
    if not zip_path.exists():
        _download_gtfs_zip(zip_path)

    extracted = _extract_gtfs_zip(zip_path, GTFS_EXTRACT_DIR)
    return str(extracted)

def _read_table(folder: str, filename: str) -> List[Dict[str, str]]:
    root = ensure_gtfs_root(folder)
    path = os.path.join(root, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    with open(path, encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [row for row in reader]

def _to_int(value: str | None) -> int | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None

def _parse_wheelchair_flag(value: str | None) -> bool | None:
    flag = _to_int(value)
    if flag == 1:
        return True
    if flag == 2:
        return False
    return None

def _unique_in_order(values: Iterable[str]) -> List[str]:
    seen = set()
    unique_values: List[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            unique_values.append(value)
    return unique_values

def load_gtfs_routes(gtfs_path: str = gtfs_path) -> List[Dict[str, str]]:
    return _read_table(gtfs_path, "routes.txt")

def load_gtfs_stops(gtfs_path: str = gtfs_path) -> List[Dict[str, str]]:
    return _read_table(gtfs_path, "stops.txt")

def load_gtfs_trips(gtfs_path: str = gtfs_path) -> List[Dict[str, str]]:
    return _read_table(gtfs_path, "trips.txt")

def load_gtfs_stop_times(gtfs_path: str = gtfs_path) -> List[Dict[str, str]]:
    return _read_table(gtfs_path, "stop_times.txt")

def get_routes_by_type(
    route_types: Sequence[int] = DEFAULT_ROUTE_TYPES,
    gtfs_path: str = gtfs_path,
) -> List[Dict[str, str]]:
    allowed_types = set(route_types)
    routes: List[Dict[str, str]] = []
    for row in load_gtfs_routes(gtfs_path):
        route_type = _to_int(row.get("route_type"))
        if route_type in allowed_types:
            routes.append(row)
    return routes

def build_gtfs_network(
    gtfs_path: str = gtfs_path,
    route_types: Sequence[int] = DEFAULT_ROUTE_TYPES,
) -> GTFSNetwork:
    routes = {
        row["route_id"]: row
        for row in get_routes_by_type(route_types, gtfs_path)
        if row.get("route_id")
    }
    stops = {
        row["stop_id"]: row 
        for row in load_gtfs_stops(gtfs_path) 
        if row.get("stop_id")
    }
    stop_times = load_gtfs_stop_times(gtfs_path)

    trip_stop_pairs: dict[str, List[tuple[int, str]]] = defaultdict(list)
    for row in stop_times:
        trip_id = row.get("trip_id", "")
        stop_id = row.get("stop_id", "")
        if not trip_id or not stop_id:
            continue
        stop_sequence = _to_int(row.get("stop_sequence")) or 0
        trip_stop_pairs[trip_id].append((stop_sequence, stop_id))

    trip_stop_ids = {
        trip_id: _unique_in_order(
            stop_id for _, stop_id in sorted(pairs, key=lambda item: item[0])
        )
        for trip_id, pairs in trip_stop_pairs.items()
    }

    route_stop_ids: dict[str, List[str]] = defaultdict(list)

    for row in load_gtfs_trips(gtfs_path):
        route_id = row.get("route_id", "")
        trip_id = row.get("trip_id", "")
        if not route_id or route_id not in routes or not trip_id:
            continue

        route_stop_ids[route_id].extend(trip_stop_ids.get(trip_id, []))

    stops_index: dict[str, GTFSStop] = {}
    routes_index: dict[str, GTFSRoute] = {}

    for route_id, route in routes.items():
        line_label = route.get("route_short_name") or route_id
        ordered_stop_ids = _unique_in_order(route_stop_ids.get(route_id, []))
        stop_rows: List[GTFSStop] = []

        for stop_id in ordered_stop_ids:
            stop_row = stops.get(stop_id, {})
            wheelchair_boarding = _parse_wheelchair_flag(stop_row.get("wheelchair_boarding"))
            stop_record = stops_index.get(stop_id)
            if stop_record is None:
                stop_record = GTFSStop(
                    id=stop_id,
                    name=stop_row.get("stop_name"),
                    lat=stop_row.get("stop_lat"),
                    lon=stop_row.get("stop_lon"),
                    wheelchair_boarding=wheelchair_boarding,
                )
                stops_index[stop_id] = stop_record

            if line_label not in stop_record.lines:
                stop_record.lines.append(line_label)

            stop_rows.append(stop_record)

        routes_index[route_id] = GTFSRoute(
            id=route_id,
            short_name=route.get("route_short_name"),
            long_name=route.get("route_long_name"),
            route_type=_to_int(route.get("route_type")),
            stops=stop_rows
        )

    return GTFSNetwork(
        routes=routes_index,
        stops=stops_index,
        route_types=list(route_types),
    )
