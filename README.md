# 서울 아파트 급매 탐지 서비스

네이버 부동산 데이터를 기반으로 서울 아파트 매매 매물의 급매를 탐지하는 웹 서비스입니다.

## 현재 구현 단계

- ✅ STEP1: FastAPI 서버/프로젝트 구조/기본 웹 페이지
- ✅ STEP2: Playwright 기반 네이버 부동산 크롤러 기본 구현
- ✅ STEP3: SQLite 저장 + TTL 캐싱 구조

## 프로젝트 구조

```text
project-root/
├── backend/
│   ├── api/         # FastAPI 엔드포인트
│   ├── crawler/     # 네이버 부동산 크롤링 로직
│   ├── database/    # SQLite 접근/저장/캐싱
│   └── services/    # 급매 분석 비즈니스 로직
├── frontend/        # 웹 UI (HTML/CSS/JS)
├── scripts/         # 실행 스크립트
├── tests/           # 테스트 코드
└── main.py          # FastAPI 진입점
```

## 로컬 실행 방법

1. 가상환경 생성 및 활성화

```bash
python -m venv .venv
source .venv/bin/activate
```

2. 의존성 설치

```bash
pip install -r requirements.txt
```

3. Playwright 브라우저 설치 (크롤링 시 필수)

```bash
python -m playwright install chromium
```

4. 서버 실행

```bash
uvicorn main:app --reload
```

5. 접속 URL

- 웹 UI: <http://127.0.0.1:8000>
- API 문서: <http://127.0.0.1:8000/docs>
- 헬스체크: <http://127.0.0.1:8000/health>

## STEP3 크롤러 + DB 저장 실행

기본 실행(크롤링 후 DB 저장 + JSON 저장):

```bash
python scripts/run_crawler.py --max-items 100 --output data/raw_listings.json
```

캐시 우선 실행(TTL 60분):

```bash
python scripts/run_crawler.py --use-cache --ttl-minutes 60 --max-items 100
```

옵션:

- `--headed`: 브라우저를 화면에 표시하며 디버깅 실행
- `--use-cache`: 최근 크롤링 결과가 신선하면 DB 캐시 조회
- `--ttl-minutes`: 캐시 신선도 판단 기준(분)

## 테스트

```bash
pytest -q
```

참고:

- `tests/test_health.py`는 `fastapi`가 없는 환경에서는 자동 skip 처리됩니다.
- DB 저장/캐시 로직은 `tests/test_database_cache.py`로 네트워크 없이 검증합니다.
