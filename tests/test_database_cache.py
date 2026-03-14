"""STEP3 SQLite 저장/캐시 로직 테스트."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.database.db import (
    get_cached_listings,
    init_db,
    is_cache_fresh,
    record_crawler_run,
    save_listings,
)


def test_save_listings_and_fetch_cache(sqlite_memory_connection) -> None:
    conn = sqlite_memory_connection
    init_db(conn)

    listings = [
        {
            "apt_name": "헬리오시티",
            "district": "송파구",
            "area_m2": 84.0,
            "price_text": "20억",
            "floor_info": "12/35",
            "title": "특가",
            "detail_url": "https://new.land.naver.com/articles/111",
        },
        {
            "apt_name": "래미안 대치팰리스",
            "district": "강남구",
            "area_m2": 84.0,
            "price_text": "23억",
            "floor_info": "10/35",
            "title": "급매",
            "detail_url": "https://new.land.naver.com/articles/222",
        },
    ]

    saved_count = save_listings(conn, listings)

    assert saved_count == 2
    cached = get_cached_listings(conn, limit=10)
    assert len(cached) == 2
    assert {row["apt_name"] for row in cached} == {"헬리오시티", "래미안 대치팰리스"}


def test_is_cache_fresh_true_when_recent(sqlite_memory_connection) -> None:
    conn = sqlite_memory_connection
    init_db(conn)
    record_crawler_run(conn, item_count=10)

    assert is_cache_fresh(conn, ttl_minutes=60) is True


def test_is_cache_fresh_false_when_expired(sqlite_memory_connection) -> None:
    conn = sqlite_memory_connection
    init_db(conn)

    old_time = datetime.now(timezone.utc) - timedelta(hours=2)
    conn.execute(
        "INSERT INTO crawler_runs (fetched_at, item_count, source) VALUES (?, ?, ?)",
        (old_time.isoformat(), 10, "naver_land"),
    )
    conn.commit()

    assert is_cache_fresh(conn, ttl_minutes=30) is False
