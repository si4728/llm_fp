import json
from pathlib import Path

from src.case_loader import load_cases


def test_load_cases_reads_json_file(tmp_path):
    case_path = tmp_path / 'cases.json'
    case_path.write_text(json.dumps([
        {
            'case_id': 'C01',
            'request': '2와 3을 더해라',
            'payload': {'a': 2, 'b': 3},
            'expected_output': 5,
            'comparison_rule': 'exact',
            'tolerance': 0,
            'error_rule': 'return_error',
            'spec_version': 'v1',
        }
    ]), encoding='utf-8')

    cases = load_cases(case_path)
    assert cases[0]['case_id'] == 'C01'
    assert cases[0]['payload']['a'] == 2
