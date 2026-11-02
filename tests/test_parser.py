import json

from src.parser import parse_json_response


def test_parse_json_response_accepts_object():
    payload = '{"result": 42, "status": "ok"}'
    result = parse_json_response(payload)
    assert result == {"result": 42, "status": "ok"}


def test_parse_json_response_raises_on_invalid():
    try:
        parse_json_response('{not valid json}')
    except ValueError:
        return
    raise AssertionError('Expected ValueError for malformed JSON')
