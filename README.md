# 서울 아파트 급매 탐지 서비스

네이버 부동산 데이터를 기반으로 서울 아파트 매매 매물의 급매를 탐지하는 웹 서비스입니다.

## STEP1 구현 범위

- FastAPI 서버 초기 구성
- 확장 가능한 프로젝트 폴더 구조 생성
- 기본 웹 페이지(초기 UI) 작성
- `/api/listings`, `/health` 기본 API 연결

## 프로젝트 구조

```text
project-root/
├── backend/
│   ├── api/
│   ├── crawler/
│   ├── database/
│   └── services/
├── frontend/
├── scripts/
├── tests/
└── main.py
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

3. Playwright 브라우저 설치 (STEP2 대비)

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

## 테스트

```bash
pytest -q
```
