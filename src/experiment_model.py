from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ModelSpec:
    key: str
    label: str
    model: str
    provider: str = 'llama_cpp'
    base_url: str = 'http://127.0.0.1:1234/v1'
    timeout: int = 180
    parameter_b: int = 13
    context_chars: int = 9000
    n_ctx: int = 8192
    n_gpu_layers: int = 0
    model_path: str = ''
    temperature: float = 0.0
    max_tokens: int = 256
    notes: str = ''


@dataclass
class ExperimentConfig:
    experiment_id: str = 'FD-20261029'
    run_id: str = 'default-run'
    phase: str = 'pilot'
    prompt_version: str = 'v1'
    temperature: float = 0.0
    seed: int | None = None
    repeats_per_case: int = 3
    model_specs: list[ModelSpec] = field(default_factory=list)
    case_filter: list[str] | None = None
    result_dir: str = 'results'
    raw_dir: str = 'results/raw'
