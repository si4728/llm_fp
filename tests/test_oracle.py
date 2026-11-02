from src.oracle import Oracle


def test_oracle_addition_case():
    oracle = Oracle()
    result = oracle.evaluate_case('C01', {'a': 2, 'b': 3})
    assert result == 5


def test_oracle_division_tolerance():
    oracle = Oracle()
    result = oracle.evaluate_case('C02', {'a': 1, 'b': 3})
    assert abs(result - 0.3333333333333333) < 1e-9
