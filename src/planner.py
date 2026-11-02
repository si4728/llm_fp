from __future__ import annotations

from typing import Any


class Planner:
    def plan(self, request: str, payload: dict[str, Any]) -> dict[str, Any]:
        request_lower = request.lower()
        task_type = 'general'

        arithmetic_tokens = ('더하', '더해', '더해라', 'add', 'sum', 'plus', '나누', 'divide', 'division', '곱', 'subtract', 'minus')
        counting_tokens = ('단어', 'word', 'count', '개수', '글자', '문자')

        if any(token in request_lower for token in arithmetic_tokens):
            task_type = 'arithmetic'
        elif any(token in request_lower for token in counting_tokens):
            task_type = 'counting'

        return {
            'task_type': task_type,
            'input': payload,
            'output_schema': {
                'type': 'object',
                'properties': {
                    'result': {'type': ['number', 'string', 'boolean']},
                    'status': {'type': 'string'}
                },
                'required': ['result', 'status']
            },
            'request': request,
        }
