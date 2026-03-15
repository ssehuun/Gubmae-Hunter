"""STEP3: 네이버 부동산 크롤링 + SQLite 저장 + 캐싱 실행 스크립트.

사용 예시:
    python scripts/run_crawler.py --max-items 50 --output data/raw_listings.json --ttl-minutes 60 --use-cache

주의:
- 로컬(특히 Windows)에서 `python scripts/run_crawler.py`로 실행할 때,
  현재 작업 디렉토리/모듈 경로 이슈로 `backend` 패키지를 못 찾는 경우가 있어
  프로젝트 루트를 sys.path에 명시적으로 추가한다.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# `python scripts/run_crawler.py` 실행 시 backend 패키지 import를 보장하기 위한 경로 보정
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.crawler.naver_land import fetch_seoul_apartment_sales
from backend.database.db import (
    get_cached_listings,
    get_connection,
    init_db,
    is_cache_fresh,
    record_crawler_run,
    save_listings,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="서울 아파트 매매 매물 크롤링/저장")
    parser.add_argument("--max-items", type=int, default=100, help="최대 수집 건수")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/raw_listings.json"),
        help="결과 JSON 저장 경로",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="브라우저 UI를 보면서 실행 (디버깅용)",
    )
    parser.add_argument(
        "--use-cache",
        action="store_true",
        help="캐시가 신선하면 크롤링 대신 DB 캐시를 사용",
    )
    parser.add_argument(
        "--ttl-minutes",
        type=int,
        default=30,
        help="캐시 신선도 기준(분)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    conn = get_connection()
    try:
        init_db(conn)

        used_cache = False
        if args.use_cache and is_cache_fresh(conn, ttl_minutes=args.ttl_minutes):
            listings = get_cached_listings(conn, limit=args.max_items)
            used_cache = True
        else:
            listings = fetch_seoul_apartment_sales(max_items=args.max_items, headless=not args.headed)
            save_listings(conn, listings)
            record_crawler_run(conn, item_count=len(listings))

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(listings, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"캐시 사용 여부: {used_cache}")
        print(f"수집/조회 매물 수: {len(listings)}")
        print(f"저장 경로: {args.output}")
    finally:
        conn.close()
