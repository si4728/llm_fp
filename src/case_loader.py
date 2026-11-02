from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_cases(path: str | Path) -> list[dict[str, Any]]:
    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding='utf-8'))
    if not isinstance(data, list):
        raise ValueError('case file must contain a list of cases')
    return data
