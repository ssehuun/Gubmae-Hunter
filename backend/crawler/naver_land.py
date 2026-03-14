"""네이버 부동산 Playwright 크롤러.

STEP2 구현 목표
- Playwright로 네이버 부동산(동적 페이지)에서 서울 아파트 매매 매물 정보를 수집
- 추후 STEP3에서 DB 저장, STEP4에서 급매 분석 로직과 연결

주의
- 네이버 페이지 구조/정책 변경에 따라 셀렉터는 변동될 수 있다.
- 로컬 실행 시 반드시 `python -m playwright install chromium` 선행 필요.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Any

# 서울 지역 진입용 기본 URL (매매/아파트 필터는 UI 상태와 URL 파라미터에 따라 달라질 수 있음)
DEFAULT_NAVER_LAND_URL = "https://new.land.naver.com/complexes"


@dataclass
class Listing:
    """크롤링으로 수집한 매물 표준 스키마."""

    apt_name: str
    district: str
    area_m2: float | None
    price_text: str
    floor_info: str
    title: str
    detail_url: str


def _safe_float(value: str | None) -> float | None:
    """문자열 숫자를 float으로 변환한다. 실패 시 None 반환."""

    if not value:
        return None

    try:
        return float(value.replace("㎡", "").strip())
    except ValueError:
        return None


def parse_article_json(raw_articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """네이버 부동산 articleList JSON 응답을 표준 매물 스키마로 정규화한다.

    Args:
        raw_articles: 네이버 부동산 API 응답의 articleList 배열

    Returns:
        표준화된 매물 딕셔너리 목록
    """

    parsed: list[dict[str, Any]] = []

    for item in raw_articles:
        parsed_item = Listing(
            apt_name=item.get("articleName", ""),
            district=item.get("cortarName", ""),
            area_m2=_safe_float(str(item.get("area1", "") or "")),
            price_text=item.get("dealOrWarrantPrc", ""),
            floor_info=item.get("floorInfo", ""),
            title=item.get("articleFeatureDesc", ""),
            detail_url=f"https://new.land.naver.com/articles/{item.get('articleNo', '')}",
        )
        parsed.append(asdict(parsed_item))

    return parsed


def fetch_seoul_apartment_sales(max_items: int = 100, headless: bool = True) -> list[dict[str, Any]]:
    """서울 아파트 매매 매물을 수집한다.

    구현 전략
    1) Playwright로 네이버 부동산 페이지 접속
    2) XHR/Fetch 응답 중 articleList 데이터를 수집
    3) 표준 스키마로 정규화 후 반환

    Args:
        max_items: 최대 수집 매물 수
        headless: 헤드리스 모드 여부
    """

    collected_articles: list[dict[str, Any]] = []

    # Playwright는 런타임에만 import하여, 테스트 환경(미설치)에서도 파서 테스트가 가능하게 한다.
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        def _on_response(response: Any) -> None:
            # 네이버 부동산의 article list API 패턴
            if "articles" not in response.url:
                return
            if response.request.resource_type not in {"xhr", "fetch"}:
                return

            try:
                payload = response.json()
            except Exception:
                return

            # 구조 예: {"articleList": [...]} 또는 {"body": {"articleList": [...]}}
            article_list = payload.get("articleList")
            if article_list is None and isinstance(payload.get("body"), dict):
                article_list = payload["body"].get("articleList")

            if isinstance(article_list, list):
                collected_articles.extend(article_list)

        page.on("response", _on_response)

        try:
            page.goto(DEFAULT_NAVER_LAND_URL, timeout=30_000)
            # 초기 XHR 수집 대기
            page.wait_for_timeout(5_000)
        except PlaywrightTimeoutError:
            # 타임아웃이 나더라도 이미 수집한 응답이 있다면 활용
            pass
        finally:
            context.close()
            browser.close()

    normalized = parse_article_json(collected_articles)

    # 기본 방어 로직: 빈 값 제거 + 중복 제거
    unique: dict[str, dict[str, Any]] = {}
    for row in normalized:
        key = row.get("detail_url") or json.dumps(row, ensure_ascii=False)
        if key not in unique and row.get("apt_name"):
            unique[key] = row

    return list(unique.values())[:max_items]
