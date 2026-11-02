from src.logging_store import JSONLLogger


def test_jsonl_logger_appends_record(tmp_path):
    log_path = tmp_path / 'run.jsonl'
    logger = JSONLLogger(log_path)
    logger.append({'case_id': 'C01', 'status': 'ok'})
    logger.append({'case_id': 'C02', 'status': 'fail'})

    lines = log_path.read_text(encoding='utf-8').strip().splitlines()
    assert len(lines) == 2
    assert 'C02' in lines[1]
