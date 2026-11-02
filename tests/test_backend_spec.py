from src.backend import normalize_model_spec


def test_normalize_model_spec_adds_missing_required_fields():
    spec = normalize_model_spec({'provider': 'lmstudio'})
    assert spec['key'] == 'local-lm-studio'
    assert spec['label'] == 'Local LM Studio'
    assert spec['model'] == 'local-model'
    assert spec['base_url'] == 'http://127.0.0.1:1234/v1'
