"""推荐算法的单元测试。"""
from app.main import load_cars
from app.models.questionnaire import EnergyType, Priority, Purpose, Questionnaire
from app.models.recommendation import RecommendationResult
from app.services.recommender import recommend, score_car


def _q(**kwargs) -> Questionnaire:
    defaults = {
        "budget_min": 10,
        "budget_max": 20,
        "energy_type": [],
        "purpose": Purpose.FAMILY,
        "seats": 5,
        "brand_preferences": [],
        "priority": Priority.BALANCED,
    }
    defaults.update(kwargs)
    return Questionnaire(**defaults)


def test_cars_loaded():
    cars = load_cars()
    assert len(cars) > 0


def test_score_range():
    cars = load_cars()
    for car in cars:
        r = score_car(car, _q())
        assert isinstance(r, RecommendationResult)
        assert 0 <= r.score <= 100
        assert r.reasons


def test_recommend_top_n():
    cars = load_cars()
    results = recommend(cars, _q(), top_n=3)
    assert len(results) == 3
    # 分数降序
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_budget_match_rank_first():
    """预算 15-20 万的家庭用车，宋 PLUS 应进入前 3。"""
    cars = load_cars()
    q = _q(
        budget_min=15,
        budget_max=20,
        energy_type=[EnergyType.HYBRID],
        purpose=Purpose.FAMILY,
    )
    results = recommend(cars, q, top_n=5)
    names = [f"{r.car.brand} {r.car.name}" for r in results]
    assert "比亚迪 宋 PLUS DM-i" in names


def test_offroad_purpose():
    """越野场景下坦克 300 应靠前。"""
    cars = load_cars()
    q = _q(budget_min=15, budget_max=30, purpose=Purpose.OFFROAD)
    results = recommend(cars, q, top_n=5)
    top = f"{results[0].car.brand} {results[0].car.name}"
    assert "坦克 300" in top


def test_invalid_budget_rejected_by_model():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Questionnaire(
            budget_min=20, budget_max=10, purpose=Purpose.COMMUTE
        )
