"""Car Recommender AI 应用入口。

启动：uvicorn app.main:app --reload
"""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.recommendation import Car

app = FastAPI(title=settings.app_name, version="0.1.0")

STATIC_DIR = Path(__file__).resolve().parent / "static"


@lru_cache
def load_cars() -> list[Car]:
    """加载车型库数据。"""
    with open(settings.data_path, encoding="utf-8") as f:
        raw = json.load(f)
    return [Car(**item) for item in raw]


@app.get("/health")
async def health() -> dict:
    """健康检查。"""
    return {"status": "ok", "app": settings.app_name, "car_count": len(load_cars())}


# 注册路由（延迟 import 以避免循环依赖）
from app.routers.recommend import router as recommend_router  # noqa: E402

app.include_router(recommend_router)

# 静态资源与首页
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    """返回问卷前端页面。"""
    return FileResponse(STATIC_DIR / "index.html")
