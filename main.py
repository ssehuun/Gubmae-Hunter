"""애플리케이션 진입점.

STEP1에서는 FastAPI 서버와 정적 프론트엔드 제공까지 구성한다.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router as api_router

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="서울 아파트 급매 탐지 서비스",
    description="네이버 부동산 기반 서울 아파트 급매 탐지 서비스 (STEP1 초기 세팅)",
    version="0.1.0",
)

# 향후 프론트엔드 분리/배포 환경을 고려해 CORS를 우선 허용한다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 연결
app.include_router(api_router, prefix="/api")

# 정적 파일(프론트엔드 스크립트/스타일) 서빙
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


@app.get("/", include_in_schema=False)
def read_index() -> FileResponse:
    """기본 웹 UI를 반환한다."""

    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """서버 상태 확인용 엔드포인트."""

    return {"status": "ok"}
