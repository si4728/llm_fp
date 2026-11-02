from src.backend import load_bbs_model_specs


def test_load_bbs_model_specs_reads_bbs_config():
    models = load_bbs_model_specs()
    assert isinstance(models, list)
    assert len(models) > 0
    assert any(model.get('provider') == 'llama_cpp' for model in models)
