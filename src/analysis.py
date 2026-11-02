from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import median


def summarize(values):
    if not values:
        return {'count': 0, 'mean': None, 'mode': None}
    counter = Counter(values)
    return {
        'count': len(values),
        'mean': sum(values) / len(values),
        'mode': counter.most_common(1)[0][0],
    }


def load_jsonl(path: str | Path) -> list[dict]:
    records: list[dict] = []
    target = Path(path)
    if not target.exists():
        return records

    with target.open('r', encoding='utf-8') as handle:
        for line in handle:
            text = line.strip()
            if not text:
                continue
            try:
                record = json.loads(text)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def percentile(values, percent):
    if not values:
        return 0.0
    ordered = sorted(float(v) for v in values)
    index = max(0, min(len(ordered) - 1, int((percent / 100) * len(ordered))))
    return ordered[index]


def analyze_jsonl(path: str | Path) -> dict:
    records = load_jsonl(path)
    if not records:
        return {
            'total_runs': 0,
            'models': [],
            'cases': [],
            'validator_valid_rate': 0.0,
            'validator_invalid_rate': 0.0,
            'avg_latency_ms': 0.0,
            'median_latency_ms': 0.0,
            'p95_latency_ms': 0.0,
            'error_counts': {},
        }

    latencies = [float(record.get('total_latency_ms', 0) or 0) for record in records]
    validator_counts = Counter(record.get('validator_decision') for record in records)
    error_counts = Counter(
        record.get('error_type')
        for record in records
        if record.get('error_type') is not None
    )

    return {
        'total_runs': len(records),
        'models': sorted({str(record.get('model_id', 'unknown')) for record in records}),
        'cases': sorted({str(record.get('case_id', 'unknown')) for record in records}),
        'validator_valid_rate': validator_counts.get('valid', 0) / len(records),
        'validator_invalid_rate': validator_counts.get('invalid', 0) / len(records),
        'avg_latency_ms': sum(latencies) / len(latencies),
        'median_latency_ms': median(latencies),
        'p95_latency_ms': percentile(latencies, 95),
        'error_counts': dict(sorted(error_counts.items())),
    }


def format_report(summary: dict) -> str:
    lines = [
        'Experiment summary',
        f"- total_runs: {summary['total_runs']}",
        f"- models: {', '.join(summary['models']) if summary['models'] else 'n/a'}",
        f"- cases: {', '.join(summary['cases']) if summary['cases'] else 'n/a'}",
        f"- validator_valid_rate: {summary['validator_valid_rate']:.3f}",
        f"- validator_invalid_rate: {summary['validator_invalid_rate']:.3f}",
        f"- avg_latency_ms: {summary['avg_latency_ms']:.3f}",
        f"- median_latency_ms: {summary['median_latency_ms']:.3f}",
        f"- p95_latency_ms: {summary['p95_latency_ms']:.3f}",
        f"- error_counts: {summary['error_counts'] or 'none'}",
    ]
    return '\n'.join(lines)
