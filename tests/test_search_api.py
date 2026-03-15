"""STEP5/STEP7 검색 API 테스트."""

from __future__ import annotations

import pytest

fastapi_testclient = pytest.importorskip("fastapi.testclient")

from backend.database.db import get_connection, init_db, save_listings
from main import app

TestClient = fastapi_testclient.TestClient


def _seed_db(db_path) -> None:
    conn = get_connection(db_path=db_path)
    try:
        init_db(conn)
        save_listings(
            conn,
            [
                {
                    "apt_name": "래미안 대치팰리스",
                    "district": "강남구",
                    "area_m2": 84.0,
                    "price_text": "23억",
                    "floor_info": "10/35",
                    "title": "일반매물",
                    "detail_url": "https://new.land.naver.com/articles/100",
                },
                {
                    "apt_name": "헬리오시티",
                    "district": "송파구",
                    "area_m2": 59.0,
                    "price_text": "20억",
                    "floor_info": "12/35",
                    "title": "일반매물",
                    "detail_url": "https://new.land.naver.com/articles/101",
                },
                {
                    "apt_name": "헬리오시티",
                    "district": "송파구",
                    "area_m2": 59.0,
                    "price_text": "16억",
                    "floor_info": "4/35",
                    "title": "특가",
                    "detail_url": "https://new.land.naver.com/articles/102",
                },
            ],
        )
    finally:
        conn.close()


def test_listings_search_filters(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "test_step5.db"
    _seed_db(db_path)

    # API 라우트의 DB 연결을 테스트 DB로 교체
    import backend.api.routes as routes

    monkeypatch.setattr(routes, "get_connection", lambda: get_connection(db_path=db_path))

    client = TestClient(app)

    response = client.get(
        "/api/listings",
        params={
            "district": "송파구",
            "min_price_manwon": 190000,
            "max_price_manwon": 210000,
            "min_area_m2": 50,
            "max_area_m2": 70,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 1
    assert payload["items"][0]["apt_name"] == "헬리오시티"
    assert payload["items"][0]["district"] == "송파구"


def test_listings_sorting(monkeypatch, tmp_path) -> None:
    db_path = tmp_path / "test_step7.db"
    _seed_db(db_path)

    import backend.api.routes as routes

    monkeypatch.setattr(routes, "get_connection", lambda: get_connection(db_path=db_path))

    client = TestClient(app)

    # 가격 낮은순: 16억 -> 20억 -> 23억
    price_sorted = client.get("/api/listings", params={"sort_by": "price_asc"})
    assert price_sorted.status_code == 200
    items = price_sorted.json()["items"]
    assert [row["price_manwon"] for row in items] == [160000, 200000, 230000]

    # 할인율 높은순: 헬리오시티 16억(할인율 높음) 먼저
    discount_sorted = client.get("/api/listings", params={"sort_by": "discount_desc"})
    assert discount_sorted.status_code == 200
    discount_items = discount_sorted.json()["items"]
    assert discount_items[0]["apt_name"] == "헬리오시티"
    assert discount_items[0]["price_manwon"] == 160000
