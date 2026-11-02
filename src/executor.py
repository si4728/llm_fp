from __future__ import annotations

import json
from typing import Any

from src.parser import parse_json_response
from src.planner import Planner


class Executor:
    def __init__(self, backend=None, model_spec=None):
        self.backend = backend
        self.model_spec = model_spec or {'provider': 'llama_cpp'}
        self.planner = Planner()

    def execute(self, request: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self.backend is None:
            raise ValueError('backend is required')

        plan = self.planner.plan(request, payload)
        response = self.backend.generate(
            spec=self.model_spec,
            messages=[
                {'role': 'system', 'content': '요청을 수행하고 JSON으로만 응답하세요.'},
                {'role': 'user', 'content': json.dumps({'request': request, 'payload': payload, 'plan': plan}, ensure_ascii=False)},
            ],
            temperature=0.0,
            max_tokens=256,
            timeout=30,
            response_schema=plan['output_schema'],
        )

        raw_text = getattr(response, 'content', str(response))
        parsed = parse_json_response(raw_text)

        return {
            'plan': plan,
            'raw': raw_text,
            'parsed': parsed,
        }
