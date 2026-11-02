from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


SHARED_BBS_PROVIDER = Path(__file__).resolve().parents[2] / "bbs" / "app" / "providers.py"
SHARED_BBS_MODELS = Path(__file__).resolve().parents[2] / "bbs" / "config" / "models.json"
DEFAULT_MODEL_SPEC = {
    'key': 'local-lm-studio',
    'label': 'Local LM Studio',
    'model': 'local-model',
    'provider': 'lmstudio',
    'base_url': 'http://127.0.0.1:1234/v1',
    'timeout': 180,
    'context_chars': 9000,
    'parameter_b': 13,
    'n_ctx': 8192,
    'n_gpu_layers': 0,
}


def load_bbs_model_specs(config_path: str | Path | None = None) -> list[dict[str, Any]]:
    target = Path(config_path) if config_path else SHARED_BBS_MODELS
    if not target.exists():
        raise FileNotFoundError(f'BBS 모델 설정 파일을 찾을 수 없습니다: {target}')
    data = json.loads(target.read_text(encoding='utf-8'))
    models = data.get('models', [])
    if not isinstance(models, list):
        raise ValueError('BBS 모델 설정 파일의 models 항목은 배열이어야 합니다.')
    return models


def normalize_model_spec(spec: dict[str, Any] | None) -> dict[str, Any]:
    merged = dict(DEFAULT_MODEL_SPEC)
    if isinstance(spec, dict):
        merged.update({key: value for key, value in spec.items() if value is not None})
    if not merged.get('key'):
        merged['key'] = 'local-lm-studio'
    if not merged.get('label'):
        merged['label'] = 'Local LM Studio'
    if not merged.get('model'):
        merged['model'] = 'local-model'
    if not merged.get('provider'):
        merged['provider'] = 'lmstudio'
    if not merged.get('base_url') and merged.get('provider') != 'llama_cpp':
        merged['base_url'] = 'http://127.0.0.1:1234/v1'
    if merged.get('provider') == 'llama_cpp' and not merged.get('model_path'):
        merged['model_path'] = default_bbs_model_path()
    return merged


def default_bbs_model_path() -> str:
    models = load_bbs_model_specs()
    if not models:
        raise ValueError('BBS 모델 설정에 모델이 없습니다.')
    return str(models[0].get('model_path', ''))


def load_shared_llm_module():
    if not SHARED_BBS_PROVIDER.exists():
        raise FileNotFoundError(
            "BBS LLM 모듈을 찾을 수 없습니다. "
            f"공유 대상 경로: {SHARED_BBS_PROVIDER}"
        )

    spec = importlib.util.spec_from_file_location("bbs_shared_llm_providers", SHARED_BBS_PROVIDER)
    if spec is None or spec.loader is None:
        raise ImportError(f"LLM 모듈을 로드할 수 없습니다: {SHARED_BBS_PROVIDER}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_shared_llm = load_shared_llm_module()
LocalModels = _shared_llm.LocalModels
ModelError = _shared_llm.ModelError
Reply = _shared_llm.Reply


class SharedBackend:
    def __init__(self, config_path: str | Path):
        self.config_path = Path(config_path)
        self.models = LocalModels(self.config_path)

    def list_models(self):
        return self.models.list()

    def generate(self, spec, messages, temperature=0.0, max_tokens=128, timeout=None, response_schema=None):
        spec = normalize_model_spec(spec)
        return self.models.generate(
            spec,
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            response_schema=response_schema,
        )
