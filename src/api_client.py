import json
import os
import dotenv
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://futar.bkk.hu/api/query/v1/ws"

def load_api_key() -> str:
	if dotenv.load_dotenv():
		return os.getenv("API_KEY", "")

API_KEY = load_api_key()

def fetch_json(url: str, params: dict[str, Any] | None = None, timeout: int = 30) -> Any:
	if params is None:
		params = {}
	
	if API_KEY:
		params["key"] = API_KEY
	
	query = urlencode(params)
	full_url = f"{url}?{query}"

	request = Request(full_url, headers={"Accept": "application/json"})
	with urlopen(request, timeout=timeout) as response:
		payload = response.read().decode("utf-8")
		return json.loads(payload)
