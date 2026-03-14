"""SQLite 데이터베이스 접근 계층.

STEP1에서는 연결 유틸리티만 제공한다.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "listings.db"


def get_connection() -> sqlite3.Connection:
    """SQLite 연결 객체를 반환한다.

    데이터 디렉토리가 없다면 자동 생성한다.
    """

    DATA_DIR.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)
