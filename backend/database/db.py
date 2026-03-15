"""SQLite 데이터베이스 접근 계층.

STEP3/STEP5 구현 내용
- listings 테이블 생성/업데이트
- 크롤링 실행 이력(crawler_runs) 저장
- TTL 기반 캐시 사용 가능 여부 판단
- 검색 필터(구/아파트명/평형) 조회
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "listings.db"


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """SQLite 연결 객체를 반환한다.

    Args:
        db_path: 테스트 등에서 사용자 지정 DB 경로가 필요할 때 사용
    """

    DATA_DIR.mkdir(exist_ok=True)
    target_path = db_path or DB_PATH
    connection = sqlite3.connect(target_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(conn: sqlite3.Connection) -> None:
    """STEP3용 테이블을 생성한다."""

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            apt_name TEXT NOT NULL,
            district TEXT NOT NULL,
            area_m2 REAL,
            price_text TEXT NOT NULL,
            floor_info TEXT,
            title TEXT,
            detail_url TEXT NOT NULL UNIQUE,
            fetched_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS crawler_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fetched_at TEXT NOT NULL,
            item_count INTEGER NOT NULL,
            source TEXT NOT NULL
        )
        """
    )

    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_apt_area ON listings (apt_name, area_m2)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_district ON listings (district)")
    conn.commit()


def save_listings(conn: sqlite3.Connection, listings: list[dict[str, Any]]) -> int:
    """매물 목록을 DB에 저장(UPSERT)한다.

    `detail_url`을 자연키로 사용해 기존 매물을 갱신한다.

    Returns:
        처리된(삽입/업데이트 시도) 건수
    """

    if not listings:
        return 0

    now = datetime.now(timezone.utc).isoformat()

    conn.executemany(
        """
        INSERT INTO listings (
            apt_name, district, area_m2, price_text, floor_info, title, detail_url, fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(detail_url) DO UPDATE SET
            apt_name=excluded.apt_name,
            district=excluded.district,
            area_m2=excluded.area_m2,
            price_text=excluded.price_text,
            floor_info=excluded.floor_info,
            title=excluded.title,
            fetched_at=excluded.fetched_at
        """,
        [
            (
                row.get("apt_name", ""),
                row.get("district", ""),
                row.get("area_m2"),
                row.get("price_text", ""),
                row.get("floor_info", ""),
                row.get("title", ""),
                row.get("detail_url", ""),
                now,
            )
            for row in listings
            if row.get("detail_url")
        ],
    )

    conn.commit()
    return len(listings)


def record_crawler_run(conn: sqlite3.Connection, item_count: int, source: str = "naver_land") -> None:
    """크롤러 실행 이력을 저장한다."""

    conn.execute(
        "INSERT INTO crawler_runs (fetched_at, item_count, source) VALUES (?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), item_count, source),
    )
    conn.commit()


def get_cached_listings(conn: sqlite3.Connection, limit: int = 100) -> list[dict[str, Any]]:
    """최근 수집 캐시 매물을 조회한다."""

    rows = conn.execute(
        """
        SELECT apt_name, district, area_m2, price_text, floor_info, title, detail_url, fetched_at
        FROM listings
        ORDER BY datetime(fetched_at) DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()

    return [dict(row) for row in rows]

def has_cached_listings(conn: sqlite3.Connection) -> bool:
    """캐시 매물 존재 여부를 반환한다."""

    row = conn.execute("SELECT 1 FROM listings LIMIT 1").fetchone()
    return row is not None


def search_cached_listings(
    conn: sqlite3.Connection,
    *,
    district: str | None = None,
    apt_name: str | None = None,
    min_area_m2: float | None = None,
    max_area_m2: float | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """검색 필터를 적용해 캐시 매물을 조회한다.

    가격 필터는 문자열 파싱이 필요하므로 서비스 레이어에서 처리한다.
    """

    conditions: list[str] = []
    params: list[Any] = []

    if district:
        conditions.append("district = ?")
        params.append(district)

    if apt_name:
        conditions.append("apt_name LIKE ?")
        params.append(f"%{apt_name}%")

    if min_area_m2 is not None:
        conditions.append("area_m2 >= ?")
        params.append(min_area_m2)

    if max_area_m2 is not None:
        conditions.append("area_m2 <= ?")
        params.append(max_area_m2)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    sql = f"""
        SELECT apt_name, district, area_m2, price_text, floor_info, title, detail_url, fetched_at
        FROM listings
        {where_clause}
        ORDER BY datetime(fetched_at) DESC
        LIMIT ?
    """

    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def is_cache_fresh(conn: sqlite3.Connection, ttl_minutes: int = 30) -> bool:
    """최근 크롤링 이력 기준으로 캐시 신선도를 판단한다."""

    row = conn.execute(
        "SELECT fetched_at FROM crawler_runs ORDER BY datetime(fetched_at) DESC LIMIT 1"
    ).fetchone()

    if not row:
        return False

    last_fetched_at = datetime.fromisoformat(row["fetched_at"])
    threshold = datetime.now(timezone.utc) - timedelta(minutes=ttl_minutes)
    return last_fetched_at >= threshold
