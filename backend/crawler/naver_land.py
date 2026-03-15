"""네이버 부동산 API 기반 크롤러.

STEP2 개선
- Playwright 브라우저 자동화 대신 네이버 부동산 API 응답을 직접 호출해 수집한다.
- 기본은 모바일 클러스터 목록 API(`articleList`)를 사용한다.
- 필요 시 단지 번호(`complex_no`)를 넣으면 단지별 매물 API를 사용한다.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

import httpx

MOBILE_ARTICLE_LIST_API = "https://m.land.naver.com/cluster/ajax/articleList"
COMPLEX_ARTICLE_LIST_API = "https://m.land.naver.com/complex/getComplexArticleList"
NEW_LAND_COMPLEX_API = "https://new.land.naver.com/api/complexes/{complex_no}"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Referer": "https://m.land.naver.com/",
}


@dataclass
class Listing:
    """수집 매물 표준 스키마."""

    apt_name: str
    district: str
    area_m2: float | None
    price_text: str
    floor_info: str
    title: str
    detail_url: str


def _safe_float(value: str | None) -> float | None:
    if not value:
        return None

    cleaned = value.replace("㎡", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None


def _pick(item: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def _build_detail_url(item: dict[str, Any]) -> str:
    article_no = _pick(item, "articleNo", "atclNo")
    if article_no:
        return f"https://new.land.naver.com/articles/{article_no}"
    return ""


def parse_article_json(raw_articles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """다양한 네이버 부동산 article 스키마를 표준 스키마로 정규화한다."""

    parsed: list[dict[str, Any]] = []

    for item in raw_articles:
        parsed_item = Listing(
            apt_name=_pick(item, "articleName", "atclNm", "cpNm"),
            district=_pick(item, "cortarName", "cortarNm", "dvsnNm"),
            area_m2=_safe_float(_pick(item, "area1", "spc1")),
            price_text=_pick(item, "dealOrWarrantPrc", "prc", "prcTxt"),
            floor_info=_pick(item, "floorInfo", "flrInfo", "flr"),
            title=_pick(item, "articleFeatureDesc", "atclFetrDesc", "tagList"),
            detail_url=_build_detail_url(item),
        )
        parsed.append(asdict(parsed_item))

    return parsed


def _extract_article_list(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """API 응답에서 article 배열을 추출한다."""

    for key in ("articleList", "list", "result"):
        value = payload.get(key)
        if isinstance(value, list):
            return value

    body = payload.get("body")
    if isinstance(body, dict):
        for key in ("articleList", "list", "result"):
            value = body.get(key)
            if isinstance(value, list):
                return value

    return []


def _fetch_page(
    client: httpx.Client,
    *,
    page: int,
    cortar_no: str,
    complex_no: str | None,
) -> list[dict[str, Any]]:
    """한 페이지를 API로 조회한다."""

    if complex_no:
        url = COMPLEX_ARTICLE_LIST_API
        params = {
            "hscpNo": complex_no,
            "tradTpCd": "A1",  # 매매
            "page": page,
        }
    else:
        url = MOBILE_ARTICLE_LIST_API
        params = {
            "rletTpCd": "APT",
            "tradTpCd": "A1",  # 매매
            "cortarNo": cortar_no,
            "page": page,
        }

    response = client.get(url, params=params, timeout=20.0)
    response.raise_for_status()
    payload = response.json()
    return _extract_article_list(payload)


def fetch_seoul_apartment_sales(
    max_items: int = 100,
    *,
    cortar_no: str = "1168000000",  # 강남구 기본값
    complex_no: str | None = None,
    max_pages: int = 5,
) -> list[dict[str, Any]]:
    """서울 아파트 매매 매물을 API로 수집한다."""

    collected_articles: list[dict[str, Any]] = []

    with httpx.Client(headers=DEFAULT_HEADERS, follow_redirects=True) as client:
        for page in range(1, max_pages + 1):
            articles = _fetch_page(
                client,
                page=page,
                cortar_no=cortar_no,
                complex_no=complex_no,
            )
            if not articles:
                break

            collected_articles.extend(articles)
            if len(collected_articles) >= max_items:
                break

    normalized = parse_article_json(collected_articles)

    unique: dict[str, dict[str, Any]] = {}
    for row in normalized:
        key = row.get("detail_url") or json.dumps(row, ensure_ascii=False)
        if key not in unique and row.get("apt_name"):
            unique[key] = row

    return list(unique.values())[:max_items]
