from __future__ import annotations

from src.executor import Executor
from src.validator import Validator


class Runner:
    def __init__(self, backend, model_spec=None):
        self.backend = backend
        self.model_spec = model_spec
        self.executor = Executor(backend, model_spec=model_spec)
        self.validator = Validator()

    def run_case(self, case, oracle=None):
        request = case['request']
        payload = case['payload']

        exec_result = self.executor.execute(request, payload)
        decision = self.validator.validate(request, payload, exec_result['parsed'])

        return {
            'case_id': case.get('case_id'),
            'executor': exec_result,
            'validator': decision,
            'oracle': None if oracle is None else oracle.evaluate_case(case.get('case_id'), payload),
        }
