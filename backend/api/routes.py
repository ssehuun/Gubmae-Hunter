"""API 라우트 모음.

STEP1에서는 서비스 연결 전, 기본 동작 확인용 라우트만 제공한다.
"""

from fastapi import APIRouter

router = APIRouter(tags=["listings"])


@router.get("/listings")
def get_listings() -> dict[str, list]:
    """초기 응답 스키마.

    STEP2 이후 실제 크롤링/DB 데이터 조회로 확장한다.
    """

    return {"items": []}
