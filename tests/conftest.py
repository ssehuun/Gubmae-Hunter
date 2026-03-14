"""테스트 공통 설정.

pytest 실행 시 프로젝트 루트를 import path에 추가한다.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
