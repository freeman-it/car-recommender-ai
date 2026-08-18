"""推荐相关 API 路由。"""
from fastapi import APIRouter, HTTPException

from app.models.questionnaire import Questionnaire
from app.models.recommendation import Car, RecommendationResult
from app.services.llm import generate_advice
from app.services.recommender import recommend

router = APIRouter(prefix="/api", tags=["recommend"])


@router.get("/cars")
async def list_cars() -> list[Car]:
    """查看车型库。"""
    from app.main import load_cars

    return load_cars()


@router.post("/recommend", response_model=dict)
async def create_recommendation(q: Questionnaire, top_n: int = 5) -> dict:
    """根据问卷返回 Top-N 推荐车型。"""
    from app.main import load_cars

    if q.budget_max <= q.budget_min:
        raise HTTPException(status_code=400, detail="budget_max 必须大于 budget_min")

    cars = load_cars()
    if not cars:
        raise HTTPException(status_code=500, detail="车型库为空，请先填充 app/data/cars.json")

    results: list[RecommendationResult] = recommend(cars, q, top_n=top_n)
    advice = await generate_advice(q, results)
    return {
        "count": len(results),
        "advice": advice,
        "results": [r.model_dump() for r in results],
    }
