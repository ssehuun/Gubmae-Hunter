"""STEP1 기본 서버 헬스체크 테스트.

환경에 FastAPI가 없으면 테스트를 skip 하여,
의존성 설치 불가 환경에서도 테스트 파이프라인이 깨지지 않게 한다.
"""

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")

from main import app


TestClient = fastapi_testclient.TestClient


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
