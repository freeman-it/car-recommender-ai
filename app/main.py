"""Car Recommender AI 应用入口。

启动：uvicorn app.main:app --reload
"""
import json
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.models.recommendation import Car

app = FastAPI(title=settings.app_name, version="0.1.0")

# Vue 前端构建产物目录（frontend/dist），存在时由后端托管
FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"


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

# 生产模式：托管 Vue 构建产物（需先执行 npm run build）
# 注意：/api 与 /health 路由须在其之前注册，此处 mount 会接管其余所有请求
if FRONTEND_DIST.exists():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIST, html=True),
        name="frontend",
    )
