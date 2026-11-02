# LLM Function Delegation

이 프로젝트는 BBS 전체를 복사해 쓰는 구조가 아니라, BBS의 LLM 연결 모듈만 재사용하면서 독립적인 함수 위임 실험 프로젝트를 구성합니다.

## 구조

- 독립 프로젝트: `function_delegation/`
- 재사용 모듈: `/home/onbranding/access/access/llm/bbs/app/providers.py`
- 본 프로젝트는 Planner/Executor/Validator/Oracle/Runner만 자체적으로 구현합니다.

## 공유 방식

- BBS의 웹 애플리케이션, 라우트, DB, 게시판 엔진은 사용하지 않습니다.
- LLM 호출 기능만 `providers.py`에서 로드해 재사용합니다.
- 각 모듈은 프로젝트 내부에서 별개로 작성하며 BBS와 분리됩니다.

## 실행

```bash
cd /home/onbranding/access/access/llm/function_delegation
python3 -m pytest -q
```
