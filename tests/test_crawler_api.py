"""API 기반 크롤러 동작 테스트."""

from backend.crawler import naver_land


def test_parse_article_json_mobile_schema() -> None:
    raw = [
        {
            "atclNm": "은마아파트",
            "cortarNm": "강남구",
            "spc1": "84",
            "prc": "24억",
            "flrInfo": "8/14",
            "atclFetrDesc": "가격인하",
            "atclNo": "2511111111",
        }
    ]

    parsed = naver_land.parse_article_json(raw)

    assert len(parsed) == 1
    row = parsed[0]
    assert row["apt_name"] == "은마아파트"
    assert row["district"] == "강남구"
    assert row["area_m2"] == 84.0
    assert row["price_text"] == "24억"
    assert row["floor_info"] == "8/14"
    assert row["title"] == "가격인하"
    assert row["detail_url"].endswith("2511111111")


def test_fetch_seoul_apartment_sales_with_mocked_pages(monkeypatch) -> None:
    pages = {
        1: [
            {"atclNm": "헬리오시티", "cortarNm": "송파구", "spc1": "84", "prc": "20억", "atclNo": "1"},
            {"atclNm": "헬리오시티", "cortarNm": "송파구", "spc1": "84", "prc": "19억", "atclNo": "2"},
        ],
        2: [
            {"atclNm": "래미안", "cortarNm": "강남구", "spc1": "84", "prc": "23억", "atclNo": "3"},
        ],
        3: [],
    }

    def fake_fetch_page(client, *, page, cortar_no, complex_no):
        return pages.get(page, [])

    monkeypatch.setattr(naver_land, "_fetch_page", fake_fetch_page)

    items = naver_land.fetch_seoul_apartment_sales(max_items=3)

    assert len(items) == 3
    assert [item["apt_name"] for item in items] == ["헬리오시티", "헬리오시티", "래미안"]
