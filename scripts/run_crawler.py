"""크롤링 실행 스크립트.

STEP1에서는 구조만 제공하며, STEP2 구현 이후 실제 수집이 가능하다.
"""

from backend.crawler.naver_land import fetch_seoul_apartment_sales


if __name__ == "__main__":
    listings = fetch_seoul_apartment_sales()
    print(f"수집된 매물 수: {len(listings)}")
