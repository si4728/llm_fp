from src.experiment_loop import ExperimentLoop
from src.experiment_model import ExperimentConfig, ModelSpec


class DummyBackend:
    def generate(self, spec, messages, temperature=0.0, max_tokens=128, timeout=None, response_schema=None):
        return type('Reply', (), {'content': '{"result": 5, "status": "ok"}'})()


def test_experiment_loop_runs_model_case_repeat_cycle():
    config = ExperimentConfig(
        run_id='demo-run',
        phase='pilot',
        repeats_per_case=1,
        model_specs=[ModelSpec(key='m1', label='demo', model='demo-model')],
    )
    loop = ExperimentLoop(DummyBackend(), config)
    result = loop.run()
    assert result['status'] == 'completed'
    assert result['runs'] >= 1
