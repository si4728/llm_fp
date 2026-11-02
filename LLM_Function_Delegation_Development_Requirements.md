# LLM Function Delegation 재실험 코드 개발 요구사항

버전: 1.0 | 기준일: 2026-10-29 | 목적: KCI 논문용 재현 가능한 Local LLM 함수 위임 실험

## 1. 개발 경로 및 원칙

- 참고 프로젝트(읽기 전용): `/home/onbranding/access/access/llm/bbs`
- 신규 프로젝트: `/home/onbranding/access/access/llm/function_delegation`
- 개발 환경: Linux, VS Code (`code .`), Python 3.11 이상 권장.
- **참고 경로의 실제 코드와 모델 설치 상태는 아직 확인되지 않았음.** 개발 첫 단계에서 조사한다.
- 핵심 연구: Main Program의 함수 실행을 LLM에 직접 위임한다. Python Oracle은 **사후 평가 전용**이며 Executor나 Validator에 정답을 제공하지 않는다.
- 외부 계산기, Python `eval`, 생성 코드 실행, 로컬 함수로 실제 연산 대체는 본실험 Executor에서 금지한다.
- 연구 결과를 결정적 실행 보장으로 과장하지 않는다.

## 2. 연구 질문

1. 자연어 요청으로 LLM이 함수 실행을 직접 수행할 수 있는가?
2. 동일 입력 반복 실행의 consistency와 실제 oracle correctness는 얼마나 다른가?
3. Validator의 승인/거절은 독립 Oracle 판정과 얼마나 일치하는가?
4. Planner, Executor, Validator 단계의 지연과 전체 실행 비용은 얼마인가?
5. 세 경량 Local LLM의 성능 차이는 본 테스트 범위에서 어떠한가?

## 3. 초기 코드 조사 및 환경 구성

```bash
cd /home/onbranding/access/access/llm
ls -la bbs
find bbs -maxdepth 3 -type f \( -name '*.py' -o -name '*.md' -o -name '*.yaml' \) | head -100
grep -RnE 'chat.completions|localhost:1234|ollama|transformers|llama_cpp|AutoModelForCausalLM' bbs --include='*.py' --exclude-dir='.venv' | head -100
mkdir -p function_delegation && cd function_delegation
code .
```

- `bbs`에서 모델 로딩/API 호출, prompt, 응답 포맷, timeout, JSON 처리 방식을 확인한다.
- LM Studio/OpenAI-compatible API, Ollama, transformers/llama.cpp 중 **실제 구현에 맞춰** backend adapter를 선택한다.
- 모델 ID, 서버 버전, 모델 파일/quantization, context window, 하드웨어 및 Python 패키지 버전을 기록한다.
- 비밀정보 `.env`, 인증키, 토큰은 Git에 커밋하지 않는다.

## 4. 실험 설계

- 기존 논문 모델 후보: `google/gemma-4-e2b`, `google/gemma-4-e4b`, `qwen/qwen3-1.7b`. 서버에서 실제 모델 ID와 가용성을 확인한다.
- 기존 11개 케이스 유지, 신규 9개 케이스 추가, 총 20개.
- 모델별·케이스별 30회 반복: **3 × 20 × 30 = 1,800회** 본실험.
- 파일럿: 3모델 × 3대표 케이스 × 3회 = 27회; 본실험과 별도 보관.
- 실행 단위는 사용자 요청을 Planner–Executor–Validator로 처리한 1회. API 호출 수와 구분한다.
- 모델/케이스 순서는 난수 시드를 기록하여 무작위화 또는 균형 교차 배치한다.
- 온도 0을 기본으로 하되 완전 결정성을 보장한다고 주장하지 않는다.
- 모델별 `/no_think`, JSON mode, max_tokens 변경 등은 별도 실험 조건으로 기록하며 공통 조건 결과와 섞지 않는다.
- 모델 3종이 실제 설치되지 않았다면 대체 모델을 기록하고 본실험 전에 설계를 확정한다.
- 원래 C1~C11 입력을 복구하지 못하면 재구성 케이스임을 명시한다. 과거 결과와 동일 실험으로 합치지 않는다.

### 테스트 케이스

| ID | 기능 | Oracle 규칙에서 확정할 사항 |
|---|---|---|
| C01 | 정수 덧셈 | 정수 결과 |
| C02 | 부동소수점 나눗셈 | 허용 오차 |
| C03 | 0으로 나누기 | 오류 코드 |
| C04 | 영어 단어 수 | 단어 분리 규칙 |
| C05 | 문자 수 | 공백 포함 여부 |
| C06 | 한·영 혼합 단어 수 | 다국어 토큰화 규칙 |
| C07 | 점수 등급 | 등급 경계 |
| C08 | 음수 산술 | 부호 규칙 |
| C09 | 복합 산술 | 연산 우선순위 |
| C10 | 문장 토큰 분석 | 토큰 정의 |
| C11 | 모호한 규칙 분류 | 모호성 감지/질문 반환 |
| C12 | 양수·0·음수 | 경계 0 |
| C13 | 등급 경계값 | 59/60/69/70 등 |
| C14 | 긴 문자열 길이 | 공백·줄바꿈 |
| C15 | Unicode 문자 수 | 코드포인트/그래핌 기준 |
| C16 | 소수 반올림 | 반올림 규칙 |
| C17 | 다중 논리 조건 | AND/OR 우선순위 |
| C18 | 날짜 유효성 | 윤년 |
| C19 | 정렬·중복 제거 | 정렬 방향/중복 정의 |
| C20 | JSON payload 기반 계산 | 지시문/입력 분리 |

각 케이스는 `case_id`, `request`, `payload`, `expected_output`, `schema`, `comparison_rule`, `tolerance`, `error_rule`, `spec_version`을 포함한다. Oracle 기준은 본실험 전 동결한다.

## 5. 필수 소프트웨어 모듈

| ID | 모듈 | 요구사항 |
|---|---|---|
| FR01 | `backend.py` | 공통 `generate()` 인터페이스, 모델 목록/헬스체크, 타임아웃, 원시 응답·token usage 기록 |
| FR02 | `planner.py` | 자연어 요청 분석, task type·입력·실행 계획·출력 스키마 작성 |
| FR03 | `executor.py` | LLM이 직접 연산/판단; raw 응답과 JSON 결과 모두 보존 |
| FR04 | `validator.py` | 별도 LLM 검증; Oracle 정답은 입력 금지; 승인·거절·판정 불가 구분 |
| FR05 | `parser.py` | JSON 전체 파싱 우선, 스키마 검증, 복수 JSON/설명문/절단/형식 오류 분리 |
| FR06 | `oracle.py` | 독립 deterministic 정답 판정, 수치 허용오차·Unicode·예외·분류 경계 처리 |
| FR07 | `runner.py` | CLI `check/pilot/run/resume/analyze/report`, 고유 실행 ID, 중단 후 재개, 중복 방지 |
| FR08 | `logging_store.py` | append-only JSONL, CSV, manifest, 원시 요청·응답·오류·설정·지연 저장 |
| FR09 | `analysis/` | consistency, oracle correctness, Validator 혼동행렬, 실패 유형, 지연 통계 |
| FR10 | `figures.py` | 실측 로그 기반 논문용 PNG/PDF/SVG 그림 및 표 자동 생성 |

### 응답 및 오류 처리

- 원본 출력은 절대 덮어쓰지 않는다.
- `JSON_PARSE_ERROR`, `SCHEMA_ERROR`, `TIMEOUT`, `API_ERROR`, `TRUNCATED`, `VALIDATOR_UNAVAILABLE`, `ORACLE_MISMATCH` 등을 분리한다.
- JSON 복구 파서는 선택적 실험으로만 사용하고 원본/복구 결과를 모두 기록한다.
- 실패 실행도 집계에서 조용히 제외하지 않는다. 분모 정책을 사전 정의한다.
- Validator는 `valid=true/false`와 `unavailable`을 구분한다.
- Planner/Executor/Validator가 같은 모델의 서로 다른 호출인지 다른 모델인지 기록한다.

## 6. 지표 및 분석 정의

- **Exact Consistency:** 동일 모델·케이스·조건에서 최빈 원시 결과의 반복 비율. 원시 문자열의 처리 규칙을 명시한다.
- **Normalized Consistency:** 사전 등록된 정규화 규칙 적용 후 최빈 결과 비율. 정답 판정과 분리한다.
- **Oracle Correctness:** 전체 실행 중 독립 Oracle 정답인 비율. JSON 오류/타임아웃은 별도 표기하면서 end-to-end 성공률에는 실패로 포함한다.
- **Validator Valid Rate:** Validator가 승인한 비율. 판정 불가 별도 보고.
- **혼동행렬:** Oracle 정답을 양성으로 TP(정답 승인), FP(오답 승인), FN(정답 거절), TN(오답 거절).
- **False Acceptance Rate:** `FP/(FP+TN)`; **False Rejection Rate:** `FN/(FN+TP)`. 분모 0은 NA.
- **Consistency–Correctness Gap:** 동일 집계 단위에서 두 비율 차이(percentage points).
- **Latency:** Planner, Executor, Validator, total 각각 monotonic clock으로 측정; mean, median, P95, max. P99는 30회 반복에서 불안정하므로 보조 지표로만 사용.
- 모델별·케이스별·전체 결과를 분리하고, 동일 케이스 반복을 독립 문제 수로 과장하지 않는다. 케이스 단위 신뢰구간/부트스트랩을 권장한다.
- Oracle와 Validator의 전체 평균이 같아도 실행별 판정이 같다는 뜻은 아니다.

## 7. 로그 스키마(예시)

```json
{
  "experiment_id": "FD-20261029",
  "run_id": "unique-run-id",
  "attempt_id": 1,
  "phase": "main",
  "model_id": "server-model-id",
  "model_revision": "record-if-available",
  "case_id": "C01",
  "repeat_id": 1,
  "prompt_version": "v1",
  "temperature": 0.0,
  "seed": null,
  "planner_raw": "",
  "executor_raw": "",
  "executor_parsed": null,
  "validator_raw": "",
  "validator_decision": null,
  "oracle_decision": null,
  "exact_signature": "",
  "normalized_signature": "",
  "json_parse_success": false,
  "planner_latency_ms": null,
  "executor_latency_ms": null,
  "validator_latency_ms": null,
  "total_latency_ms": null,
  "input_tokens": null,
  "output_tokens": null,
  "error_type": null
}
```

원본 응답과 설정은 필요시 별도 파일로 보관하고 해시로 연결한다. 요청 시각(wall clock)과 측정 시간(monotonic)을 분리한다.

## 8. 권장 폴더 구조

```text
function_delegation/
├── README.md
├── requirements.txt
├── .gitignore
├── config/
│   ├── backend.yaml
│   ├── models.yaml
│   ├── experiment.yaml
│   └── prompts.yaml
├── cases/
│   ├── test_cases.json
│   └── oracle_spec.json
├── src/
│   ├── backend.py
│   ├── planner.py
│   ├── executor.py
│   ├── validator.py
│   ├── parser.py
│   ├── oracle.py
│   ├── runner.py
│   └── logging_store.py
├── analysis/
│   ├── metrics.py
│   ├── confusion.py
│   ├── failures.py
│   └── figures.py
├── tests/
│   ├── test_parser.py
│   ├── test_oracle.py
│   ├── test_metrics.py
│   ├── test_resume.py
│   └── test_backend_mock.py
├── results/
└── main.py
```

## 9. 단계별 개발 및 완료 기준

| 단계 | 작업 | 통과 조건 |
|---|---|---|
| 1 | `bbs` 코드 조사 및 환경 점검 | 실제 backend/모델 ID/호출 방식 확인 |
| 2 | Backend + JSON Parser | 정상/비정상 응답 단위 테스트 통과 |
| 3 | Planner/Executor/Validator | LLM이 직접 함수 실행, 원시 결과 저장 |
| 4 | Oracle + 20개 케이스 | Oracle 경계값 테스트 전부 통과 |
| 5 | Runner + Logging + Resume | 실패 로그 보존, 중단 후 중복 없이 재개 |
| 6 | 파일럿 27회 | 설정·파싱·지연·로그 누락 점검 완료 |
| 7 | 본실험 1,800회 | 모든 시도와 실패 유형 기록, 설정 동결 |
| 8 | 통계·그림 자동화 | 원본 로그로 표/그림 동일하게 재생성 |
| 9 | 논문 검수 | Abstract·본문·표·그림의 수치 일치 |

본실험 도중 프롬프트나 모델 설정을 변경하면 새 `condition_id`와 실험 버전으로 분리한다. 실패한 시도를 성공할 때까지 재시도해 결과를 바꾸지 않는다.

## 10. 논문 산출물

- Table: 환경·모델·테스트 케이스·모델별 지표·Validator 혼동행렬·오류 유형.
- Figure: Function Delegation Architecture, Evaluation Workflow, Consistency–Correctness, Case-wise Heatmap, Latency Distribution.
- `results/raw/*.jsonl`, `results/summary/*.csv`, `results/figures/*`, `experiment_manifest.json`.
- 재현용 README, 실행 명령, prompt/version, 모델 파일 정보 및 해시, requirements 버전 기록.
- 이전 논문 결과와 새 결과는 별도 실험 버전으로 구분한다.

## 11. 개발자에게 전달할 핵심 지시

> `bbs`의 실제 Local LLM 사용 방식을 먼저 조사하라. 기존 코드를 임의로 수정하지 말고 `function_delegation` 독립 프로젝트를 만든다. LLM이 함수를 직접 수행하는 구조를 유지하며, Oracle은 사후 정답 평가에만 사용한다. 모든 요청/응답/설정/오류/지연을 보존하고, 27회 파일럿 검증 후 동결된 조건으로 1,800회 본실험을 수행할 수 있도록 구현한다. 표와 그림은 반드시 원본 실행 로그에서 자동 생성해야 한다.
