import json
import sys

from main import main


def test_cli_run_with_mock(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        'argv',
        ['main.py', 'run', '--mock', '--run-id', 'demo-run', '--phase', 'pilot', '--repeats', '1'],
    )
    main()
    output = capsys.readouterr().out
    assert 'completed' in output
    assert 'demo-run' in output
