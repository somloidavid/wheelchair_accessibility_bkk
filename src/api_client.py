import json
import os
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from dotenv import load_dotenv
from src.models.trip_model import *

load_dotenv()

BASE_URL = "https://futar.bkk.hu/api/query/v1/ws"

def load_api_key() -> str:
	return os.getenv("API_KEY", "bkk-web")

API_KEY = load_api_key()

def fetch_json(url: str, params: dict[str, Any] | None = None, payload: dict[str, Any] | None = None, timeout: int = 30) -> Any:
	if params is None:
		params = {}
	
	if API_KEY:
		params["key"] = API_KEY
	
	query = urlencode(params)
	full_url = f"{BASE_URL}/{url}?{query}"

	headers = {"Accept": "application/json"}
	data = None

	if payload is not None:
		data = json.dumps(payload).encode("utf-8")
		headers["Content-Type"] = "application/json"

	request = Request(full_url, data=data, headers=headers)
	with urlopen(request, timeout=timeout) as response:
		response_data = response.read().decode("utf-8")
		return json.loads(response_data)

def plan_trip(fromPlace: str, toPlace: str, mode: list[str], wheelchair_accessible: bool = False):
	json_response = fetch_json(
		"otp/api/where/plan-trip",
		params={
			"fromPlace": fromPlace,
			"toPlace": toPlace,
			"mode": ",".join(mode),
			"includeReferences": "stops",
			"wheelchair": wheelchair_accessible
		})
	return TripResponse(**json_response)