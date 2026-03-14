"""네이버 부동산 크롤러.

STEP1에서는 Playwright 기반 크롤러 구조만 준비한다.
"""

from typing import Any


def fetch_seoul_apartment_sales() -> list[dict[str, Any]]:
    """서울 아파트 매매 데이터를 수집해 반환한다.

    STEP2에서 Playwright 구현을 추가한다.
    """

    # 추후 반환 예시:
    # [{"apt_name": "...", "price": 120000, "area": 84.99, ...}]
    return []
