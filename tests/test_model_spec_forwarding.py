from src.executor import Executor
from src.runner import Runner


class DummyBackend:
    def __init__(self):
        self.last_spec = None

    def generate(self, spec, messages, temperature=0.0, max_tokens=128, timeout=None, response_schema=None):
        self.last_spec = spec
        return type('Reply', (), {'content': '{"result": 5, "status": "ok"}'})()


def test_runner_passes_selected_model_spec_to_backend():
    backend = DummyBackend()
    runner = Runner(backend, model_spec={'key': 'Gemma_Local_1', 'provider': 'llama_cpp', 'model_path': '/tmp/test.gguf'})
    runner.run_case({'case_id': 'C01', 'request': '2와 3을 더해라', 'payload': {'a': 2, 'b': 3}}, oracle=None)
    assert backend.last_spec['provider'] == 'llama_cpp'
    assert backend.last_spec['model_path'] == '/tmp/test.gguf'
