"""API 라우트 모음.

STEP7에서는 검색 필터 + 정렬(가격 낮은순/할인율 높은순)을 지원한다.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from backend.database.db import get_connection, init_db, search_cached_listings
from backend.services.quick_sale import analyze_quick_sale

router = APIRouter(tags=["listings"])


@router.get("/listings")
def get_listings(
    limit: int = Query(default=100, ge=1, le=1000),
    district: str | None = None,
    apt_name: str | None = None,
    min_price_manwon: int | None = Query(default=None, ge=0),
    max_price_manwon: int | None = Query(default=None, ge=0),
    min_area_m2: float | None = Query(default=None, ge=0),
    max_area_m2: float | None = Query(default=None, ge=0),
    sort_by: str | None = Query(default=None, pattern="^(price_asc|discount_desc)?$"),
) -> dict[str, list]:
    """검색 필터/정렬을 적용한 매물을 조회하고 급매 분석 필드를 포함해 반환한다."""

    conn = get_connection()
    try:
        init_db(conn)
        listings = search_cached_listings(
            conn,
            district=district,
            apt_name=apt_name,
            min_area_m2=min_area_m2,
            max_area_m2=max_area_m2,
            limit=limit,
        )
        analyzed = analyze_quick_sale(listings)

        # 가격 문자열은 서비스에서 파싱한 price_manwon 기준으로 필터 적용
        filtered = []
        for row in analyzed:
            price_manwon = row.get("price_manwon")
            if min_price_manwon is not None and (price_manwon is None or price_manwon < min_price_manwon):
                continue
            if max_price_manwon is not None and (price_manwon is None or price_manwon > max_price_manwon):
                continue
            filtered.append(row)

        # STEP7 정렬
        if sort_by == "price_asc":
            filtered.sort(key=lambda x: x.get("price_manwon") if x.get("price_manwon") is not None else 10**12)
        elif sort_by == "discount_desc":
            filtered.sort(
                key=lambda x: x.get("discount_rate") if x.get("discount_rate") is not None else -10**12,
                reverse=True,
            )

        return {"items": filtered}
    finally:
        conn.close()
