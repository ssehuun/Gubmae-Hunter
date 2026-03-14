"""STEP1 기본 서버 헬스체크 테스트."""

from fastapi.testclient import TestClient

from main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
