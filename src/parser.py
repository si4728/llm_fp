import json
from typing import Any


def parse_json_response(raw: Any) -> Any:
    if raw is None:
        raise ValueError("JSON_PARSE_ERROR: empty response")
    if isinstance(raw, (dict, list, int, float, bool)):
        return raw
    text = str(raw).strip()
    if not text:
        raise ValueError("JSON_PARSE_ERROR: empty response")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("JSON_PARSE_ERROR") from exc
