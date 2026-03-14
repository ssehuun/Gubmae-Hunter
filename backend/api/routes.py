"""API 라우트 모음.

STEP4에서는 DB 캐시 매물에 급매 분석 로직을 적용해 반환한다.
"""

from __future__ import annotations

from fastapi import APIRouter

from backend.database.db import get_cached_listings, get_connection, init_db
from backend.services.quick_sale import analyze_quick_sale

router = APIRouter(tags=["listings"])


@router.get("/listings")
def get_listings(limit: int = 100) -> dict[str, list]:
    """캐시된 매물을 조회하고 급매 분석 필드를 포함해 반환한다."""

    conn = get_connection()
    try:
        init_db(conn)
        listings = get_cached_listings(conn, limit=limit)
        analyzed = analyze_quick_sale(listings)
        return {"items": analyzed}
    finally:
        conn.close()
