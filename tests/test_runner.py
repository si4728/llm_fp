from src.executor import Executor
from src.planner import Planner
from src.runner import Runner
from src.validator import Validator


class DummyBackend:
    def __init__(self, reply):
        self.reply = reply

    def generate(self, spec, messages, temperature=0.0, max_tokens=128, timeout=None, response_schema=None):
        return type('Reply', (), {'content': self.reply})()


def test_planner_creates_plan():
    planner = Planner()
    plan = planner.plan('2와 3을 더해라', {'a': 2, 'b': 3})
    assert plan['task_type'] == 'arithmetic'
    assert plan['output_schema']['type'] == 'object'


def test_executor_parses_backend_response():
    exec_mod = Executor(DummyBackend('{"result": 5, "status": "ok"}'))
    result = exec_mod.execute('2와 3을 더해라', {'a': 2, 'b': 3})
    assert result['parsed']['result'] == 5


def test_validator_accepts_good_result():
    validator = Validator()
    decision = validator.validate('2와 3을 더해라', {'a': 2, 'b': 3}, {'result': 5})
    assert decision['decision'] == 'valid'


def test_runner_orchestrates_case():
    dummy_backend = DummyBackend('{"result": 5, "status": "ok"}')
    runner = Runner(dummy_backend)
    result = runner.run_case({'case_id': 'C01', 'request': '2와 3을 더해라', 'payload': {'a': 2, 'b': 3}}, oracle=None)
    assert result['executor']['parsed']['result'] == 5
    assert result['validator']['decision'] == 'valid'
