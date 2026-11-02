from src.analysis import analyze_jsonl, summarize


def test_summarize_returns_mean_and_mode():
    summary = summarize([1, 2, 2, 3])
    assert summary['count'] == 4
    assert summary['mean'] == 2.0
    assert summary['mode'] == 2


def test_analyze_jsonl_builds_summary(tmp_path):
    log_path = tmp_path / 'sample.jsonl'
    log_path.write_text(
        '\n'.join([
            '{"model_id": "m1", "case_id": "C01", "validator_decision": "valid", "oracle_decision": 5, "error_type": null, "total_latency_ms": 10}',
            '{"model_id": "m1", "case_id": "C02", "validator_decision": "valid", "oracle_decision": 7, "error_type": null, "total_latency_ms": 20}',
            '{"model_id": "m2", "case_id": "C01", "validator_decision": "invalid", "oracle_decision": 0, "error_type": "TIMEOUT", "total_latency_ms": 200}',
        ]) + '\n',
        encoding='utf-8',
    )

    summary = analyze_jsonl(log_path)

    assert summary['total_runs'] == 3
    assert summary['validator_valid_rate'] == 2 / 3
    assert summary['models'] == ['m1', 'm2']
    assert summary['error_counts']['TIMEOUT'] == 1
    assert summary['avg_latency_ms'] == 76.66666666666667
