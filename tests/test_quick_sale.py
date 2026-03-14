"""STEP4 급매 탐지 로직 테스트."""

from backend.services.quick_sale import analyze_quick_sale, parse_price_to_manwon


def test_parse_price_to_manwon() -> None:
    assert parse_price_to_manwon("23억") == 230000
    assert parse_price_to_manwon("23억 5,000") == 235000
    assert parse_price_to_manwon("8억2,500") == 82500
    assert parse_price_to_manwon("120000") == 120000


def test_analyze_quick_sale_by_discount_and_lowest_and_keyword() -> None:
    listings = [
        {
            "apt_name": "래미안",
            "district": "강남구",
            "area_m2": 84.0,
            "price_text": "10억",
            "floor_info": "10/20",
            "title": "일반매물",
            "detail_url": "u1",
        },
        {
            "apt_name": "래미안",
            "district": "강남구",
            "area_m2": 84.0,
            "price_text": "8억",
            "floor_info": "2/20",
            "title": "급매 빠른매도",
            "detail_url": "u2",
        },
    ]

    analyzed = analyze_quick_sale(listings, discount_threshold=5.0)

    first, second = analyzed
    assert first["is_quick_sale"] is False
    assert second["is_quick_sale"] is True
    assert second["keyword_matched"] is True
    assert second["is_lowest_price"] is True
    assert second["discount_rate"] == 11.11
