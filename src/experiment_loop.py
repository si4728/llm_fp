from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from src.case_loader import load_cases
from src.experiment_model import ExperimentConfig, ModelSpec
from src.logging_store import JSONLLogger
from src.oracle import Oracle
from src.runner import Runner


class ExperimentLoop:
    def __init__(self, backend, config: ExperimentConfig):
        self.backend = backend
        self.config = config
        self.oracle = Oracle()

    def run(self):
        case_path = Path('cases/test_cases.json')
        cases = load_cases(case_path)
        if self.config.case_filter:
            cases = [c for c in cases if c.get('case_id') in self.config.case_filter]

        raw_dir = Path(self.config.raw_dir)
        raw_dir.mkdir(parents=True, exist_ok=True)
        logger = JSONLLogger(raw_dir / f'{self.config.run_id}.jsonl')

        for model in self.config.model_specs:
            for case in cases:
                for repeat_id in range(1, self.config.repeats_per_case + 1):
                    run_start = time.perf_counter()
                    result = Runner(self.backend, model_spec={
                        'key': model.key,
                        'label': model.label,
                        'model': model.model,
                        'provider': model.provider,
                        'base_url': model.base_url,
                        'timeout': model.timeout,
                        'parameter_b': model.parameter_b,
                        'context_chars': model.context_chars,
                        'n_ctx': model.n_ctx,
                        'n_gpu_layers': model.n_gpu_layers,
                        'model_path': model.model_path,
                    }).run_case(case, oracle=self.oracle)
                    elapsed = time.perf_counter() - run_start

                    record = {
                        'experiment_id': self.config.experiment_id,
                        'run_id': self.config.run_id,
                        'phase': self.config.phase,
                        'model_id': model.model,
                        'case_id': case.get('case_id'),
                        'repeat_id': repeat_id,
                        'prompt_version': self.config.prompt_version,
                        'temperature': self.config.temperature,
                        'seed': self.config.seed,
                        'total_latency_ms': round(elapsed * 1000, 3),
                        'executor_parsed': result['executor']['parsed'],
                        'validator_decision': result['validator']['decision'],
                        'oracle_decision': result['oracle'],
                        'error_type': None,
                    }
                    logger.append(record)

        return {
            'status': 'completed',
            'run_id': self.config.run_id,
            'phase': self.config.phase,
            'runs': len(cases) * self.config.repeats_per_case * len(self.config.model_specs),
        }
