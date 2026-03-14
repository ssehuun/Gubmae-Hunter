"""급매 탐지 서비스 레이어.

STEP1에서는 인터페이스(함수 시그니처)만 정의한다.
"""

from typing import Any


def analyze_quick_sale(listings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """매물 목록을 입력받아 급매 관련 필드를 계산한다.

    실제 구현은 STEP4에서 진행한다.
    """

    return listings
