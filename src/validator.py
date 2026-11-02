from __future__ import annotations

from typing import Any


class Validator:
    def validate(self, request: str, payload: dict[str, Any], result: Any) -> dict[str, Any]:
        if isinstance(result, dict):
            if result.get('status') == 'ok':
                return {'decision': 'valid', 'reason': 'result has ok status'}
            if result.get('status') == 'error':
                return {'decision': 'invalid', 'reason': 'result marked error'}

        # 안전한 기본 판정: 값이 비어있지 않으면 승인한다.
        if result is not None:
            return {'decision': 'valid', 'reason': 'result is present'}

        return {'decision': 'invalid', 'reason': 'empty result'}
