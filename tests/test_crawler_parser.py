"""STEP2 크롤러 파서 단위 테스트."""

from backend.crawler.naver_land import parse_article_json


def test_parse_article_json_maps_fields() -> None:
    raw = [
        {
            "articleName": "래미안 대치팰리스",
            "cortarName": "강남구",
            "area1": "84",
            "dealOrWarrantPrc": "23억",
            "floorInfo": "10/35",
            "articleFeatureDesc": "급매",
            "articleNo": "2412345678",
        }
    ]

    parsed = parse_article_json(raw)

    assert len(parsed) == 1
    row = parsed[0]
    assert row["apt_name"] == "래미안 대치팰리스"
    assert row["district"] == "강남구"
    assert row["area_m2"] == 84.0
    assert row["price_text"] == "23억"
    assert row["floor_info"] == "10/35"
    assert row["title"] == "급매"
    assert row["detail_url"].endswith("2412345678")
