from __future__ import annotations

import json
from urllib.request import Request, urlopen

def fetch_json(url: str):
	request = Request(url, headers={"Accept": "application/json"})
	with urlopen(request, timeout=30) as response:
		payload = response.read().decode("utf-8")
		return json.loads(payload)