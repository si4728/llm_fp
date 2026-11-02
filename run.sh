#!/usr/bin/env bash
set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BBS_DIR="$(cd "$PROJECT_DIR/../bbs" && pwd)"
BBS_VENV="$BBS_DIR/.venv"
MODELS=(Gemma_Local_1 GPT_Local_1 Qween3_Local_3)
PILOT_REPEATS="${PILOT_REPEATS:-3}"
MAIN_REPEATS="${MAIN_REPEATS:-30}"

cd "$PROJECT_DIR"

if [ ! -d "$BBS_VENV" ]; then
  echo "BBS venv not found at $BBS_VENV" >&2
  exit 1
fi

run_all_models() {
  local phase="$1"
  local repeats="$2"
  for model in "${MODELS[@]}"; do
    local run_id="${phase}-${model}"
    echo "=== ${phase}: ${model} ==="
    python main.py run --run-id "$run_id" --phase "$phase" --repeats "$repeats" --model "$model"
    echo
    echo "=== report: ${run_id} ==="
    python main.py report --run-id "$run_id"
    echo
  done
}

if [ "${1:-}" = "all" ]; then
  shift || true
  . "$BBS_VENV/bin/activate"
  run_all_models "pilot" "$PILOT_REPEATS"
  run_all_models "main" "$MAIN_REPEATS"
  exit 0
fi

if [ "${1:-}" = "pilot" ]; then
  shift || true
  . "$BBS_VENV/bin/activate"
  run_all_models "pilot" "$PILOT_REPEATS"
  exit 0
fi

if [ "${1:-}" = "main" ]; then
  shift || true
  . "$BBS_VENV/bin/activate"
  run_all_models "main" "$MAIN_REPEATS"
  exit 0
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
fi

. "$BBS_VENV/bin/activate"
python -m pip install -q -r requirements.txt
python main.py "$@"
