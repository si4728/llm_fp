from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.analysis import analyze_jsonl, format_report
from src.backend import SharedBackend, load_bbs_model_specs
from src.case_loader import load_cases
from src.experiment_loop import ExperimentLoop
from src.experiment_model import ExperimentConfig, ModelSpec


class MockBackend:
    def generate(self, spec, messages, temperature=0.0, max_tokens=128, timeout=None, response_schema=None):
        class Reply:
            content = '{"result": 5, "status": "ok"}'

        return Reply()


def build_parser():
    parser = argparse.ArgumentParser(description='LLM function delegation experiment runner')
    parser.add_argument('command', choices=['check', 'pilot', 'run', 'resume', 'analyze', 'report'], help='실행 명령')
    parser.add_argument('--cases', default='cases/test_cases.json', help='테스트 케이스 JSON 경로')
    parser.add_argument('--run-id', default='demo-run', help='실험 run ID')
    parser.add_argument('--phase', default='pilot', help='실험 phase')
    parser.add_argument('--repeats', type=int, default=1, help='각 케이스 반복 횟수')
    parser.add_argument('--model', default=None, help='모델 키. 기본값은 BBS의 첫 모델을 사용합니다.')
    parser.add_argument('--mock', action='store_true', help='로컬 LLM 서버 없이 mock 응답으로 실험을 실행')
    parser.add_argument('--log', default=None, help='분석할 JSONL 로그 경로. 기본값은 results/raw/<run-id>.jsonl 입니다.')
    return parser


def resolve_log_path(run_id: str, log_path: str | None) -> Path | None:
    if log_path:
        candidate = Path(log_path)
        if candidate.exists():
            return candidate
        raise FileNotFoundError(f'로그 파일을 찾을 수 없습니다: {candidate}')

    candidate = Path('results/raw') / f'{run_id}.jsonl'
    if candidate.exists():
        return candidate

    latest = sorted(Path('results/raw').glob('*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)
    return latest[0] if latest else None


def main() -> None:
    args = build_parser().parse_args()

    if args.command == 'check':
        cases = load_cases(args.cases)
        print(f'Loaded {len(cases)} cases from {args.cases}')
        return

    backend = MockBackend() if args.mock else SharedBackend('/home/onbranding/access/access/llm/bbs/config/models.json')
    bbs_models = load_bbs_model_specs()
    selected_model_name = args.model or bbs_models[0]['key']
    selected_model = next((m for m in bbs_models if m.get('key') == selected_model_name), bbs_models[0])
    model = ModelSpec(
        key=selected_model.get('key', selected_model_name),
        label=selected_model.get('label', selected_model_name),
        model=selected_model.get('model', selected_model_name),
        provider=selected_model.get('provider', 'llama_cpp'),
        base_url=selected_model.get('base_url', 'http://127.0.0.1:1234/v1'),
        timeout=int(selected_model.get('timeout', 180)),
        parameter_b=float(selected_model.get('parameter_b', 13)),
        context_chars=int(selected_model.get('context_chars', 9000)),
        n_ctx=int(selected_model.get('n_ctx', 8192)),
        n_gpu_layers=int(selected_model.get('n_gpu_layers', 0)),
        model_path=selected_model.get('model_path', ''),
    )
    config = ExperimentConfig(
        run_id=args.run_id,
        phase=args.phase,
        repeats_per_case=args.repeats,
        model_specs=[model],
    )

    if args.command in {'pilot', 'run'}:
        result = ExperimentLoop(backend, config).run()
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if args.command == 'resume':
        print('resume is not yet implemented in this prototype.')
        return

    if args.command == 'analyze':
        log_path = resolve_log_path(args.run_id, args.log)
        if log_path is None:
            print(json.dumps({'total_runs': 0, 'models': [], 'cases': [], 'error_counts': {}}, ensure_ascii=False, indent=2))
            return
        summary = analyze_jsonl(log_path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if args.command == 'report':
        log_path = resolve_log_path(args.run_id, args.log)
        if log_path is None:
            print('No experiment log found.')
            return
        summary = analyze_jsonl(log_path)
        print(format_report(summary))
        return


if __name__ == '__main__':
    main()
