"""급매 탐지 서비스 레이어 (STEP4).

급매 판단 기준
1) 제목 키워드 포함 여부
2) 동일 단지 + 동일 평형 평균 대비 할인율
3) 동일 단지 + 동일 평형 최저가 여부
"""

from __future__ import annotations

import re
from typing import Any

QUICK_SALE_KEYWORDS = ["급매", "특가", "빠른매도", "가격인하"]


def parse_price_to_manwon(price_text: str) -> int | None:
    """가격 문자열을 만원 단위 정수로 변환한다.

    예:
    - "23억" -> 230000
    - "23억 5,000" -> 235000
    - "8억2,500" -> 82500
    - "120000" -> 120000
    """

    if not price_text:
        return None

    normalized = price_text.replace(",", "").replace(" ", "")

    # '23억5000' 또는 '23억' 형태
    match = re.match(r"^(\d+)억(?:(\d+))?$", normalized)
    if match:
        eok = int(match.group(1))
        man = int(match.group(2)) if match.group(2) else 0
        return eok * 10_000 + man

    # 숫자만 들어오는 경우(이미 만원 단위라고 가정)
    if normalized.isdigit():
        return int(normalized)

    return None


def _contains_keyword(title: str) -> bool:
    return any(keyword in (title or "") for keyword in QUICK_SALE_KEYWORDS)


def analyze_quick_sale(listings: list[dict[str, Any]], discount_threshold: float = 5.0) -> list[dict[str, Any]]:
    """매물 목록을 입력받아 급매 판단 필드를 계산한다.

    Returns:
        각 매물에 아래 필드를 추가한 리스트
        - price_manwon
        - avg_price_manwon
        - min_price_manwon
        - discount_rate
        - keyword_matched
        - is_lowest_price
        - is_quick_sale
    """

    enriched: list[dict[str, Any]] = []
    grouped_prices: dict[tuple[str, Any], list[int]] = {}

    # 1차: 가격 파싱 + 그룹 구성
    for item in listings:
        copied = dict(item)
        price_manwon = parse_price_to_manwon(str(copied.get("price_text", "")))
        copied["price_manwon"] = price_manwon

        group_key = (str(copied.get("apt_name", "")).strip(), copied.get("area_m2"))
        if group_key[0] and isinstance(price_manwon, int):
            grouped_prices.setdefault(group_key, []).append(price_manwon)

        enriched.append(copied)

    # 2차: 평균/최저/할인율/급매 여부 계산
    for item in enriched:
        group_key = (str(item.get("apt_name", "")).strip(), item.get("area_m2"))
        prices = grouped_prices.get(group_key, [])
        current_price = item.get("price_manwon")

        avg_price = sum(prices) / len(prices) if prices else None
        min_price = min(prices) if prices else None

        discount_rate = None
        if isinstance(current_price, int) and avg_price and avg_price > 0:
            discount_rate = round(((avg_price - current_price) / avg_price) * 100, 2)

        keyword_matched = _contains_keyword(str(item.get("title", "")))
        is_lowest_price = bool(isinstance(current_price, int) and min_price is not None and current_price == min_price)
        is_discounted = bool(discount_rate is not None and discount_rate >= discount_threshold)

        item["avg_price_manwon"] = int(avg_price) if avg_price is not None else None
        item["min_price_manwon"] = min_price
        item["discount_rate"] = discount_rate
        item["keyword_matched"] = keyword_matched
        item["is_lowest_price"] = is_lowest_price
        item["is_quick_sale"] = keyword_matched or is_discounted or is_lowest_price

    return enriched
