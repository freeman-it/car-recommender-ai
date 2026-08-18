"""核心推荐算法：基于问卷的多维度加权评分。"""
from app.models.questionnaire import EnergyType, Priority, Purpose, Questionnaire
from app.models.recommendation import Car, RecommendationResult

# 各维度满分
PRICE_SCORE = 40
ENERGY_SCORE = 15
SEATS_SCORE = 15
PURPOSE_SCORE = 15
BRAND_SCORE = 10
PRIORITY_SCORE = 5

# 场景 -> 关键标签（评分时命中的标签权重更高）
PURPOSE_TAGS: dict[Purpose, list[str]] = {
    Purpose.COMMUTE: ["代步", "经济", "小车"],
    Purpose.FAMILY: ["大空间", "家用", "安全"],
    Purpose.BUSINESS: ["商务", "豪华", "舒适"],
    Purpose.SPORT: ["运动", "性能", "操控"],
    Purpose.OFFROAD: ["越野", "四驱", "通过性"],
}

# 优先级 -> 评分时额外关注的参数
PRIORITY_SPECS: dict[Priority, list[str]] = {
    Priority.SPACE: ["轴距", "后备箱"],
    Priority.POWER: ["马力", "加速"],
    Priority.ECONOMY: ["油耗", "续航"],
    Priority.TECH: ["智能", "辅助驾驶"],
    Priority.SAFETY: ["安全", "气囊"],
    Priority.VALUE: ["保值", "品牌"],
    Priority.BALANCED: [],
}


def _score_price(car: Car, q: Questionnaire) -> tuple[float, str]:
    """价格得分：落在预算区间内得分最高，越贴近区间中点越好。"""
    price = car.price
    if q.budget_min <= price <= q.budget_max:
        # 区间内：越接近中点分越高（34-40）
        deviation = abs(price - q.budget_mid) / q.budget_span
        score = PRICE_SCORE * (1 - 0.15 * deviation)
        reason = f"价格 {price:.1f} 万元在预算 {q.budget_min:.0f}-{q.budget_max:.0f} 万元内"
        return score, reason
    if price < q.budget_min:
        # 低于预算：可接受但分低，越便宜扣越多
        score = PRICE_SCORE * 0.5
        reason = f"价格 {price:.1f} 万元低于预算下限，可能配置/级别偏低"
        return score, reason
    # 高于预算
    over = (price - q.budget_max) / max(q.budget_max, 1)
    score = PRICE_SCORE * max(0.1, 0.4 - 0.5 * over)
    reason = f"价格 {price:.1f} 万元超出预算上限 {q.budget_max:.0f} 万元"
    return score, reason


def _score_energy(car: Car, q: Questionnaire) -> tuple[float, str]:
    """能源类型得分。"""
    if not q.energy_type:
        return ENERGY_SCORE, "未限定能源类型"
    car_energy = car.energy_type
    accepted = [e.value for e in q.energy_type]
    if car_energy in accepted:
        return ENERGY_SCORE, f"能源类型（{car_energy}）符合要求"
    if EnergyType.HYBRID.value in accepted:
        # 用户接受混动时，纯电/燃油降级但可用
        return ENERGY_SCORE * 0.7, f"非首选能源（{car_energy}），与混动偏好有差距"
    return ENERGY_SCORE * 0.3, f"能源类型（{car_energy}）与要求不符"


def _score_seats(car: Car, q: Questionnaire) -> tuple[float, str]:
    """座位数得分。"""
    if car.seats >= q.seats:
        return SEATS_SCORE, f"提供 {car.seats} 座，满足 {q.seats} 座需求"
    return SEATS_SCORE * 0.3, f"仅 {car.seats} 座，不满足 {q.seats} 座需求"


def _score_purpose(car: Car, q: Questionnaire) -> tuple[float, str]:
    """场景匹配得分：命中场景关键标签越多分越高。"""
    key_tags = PURPOSE_TAGS.get(q.purpose, [])
    hit = sum(1 for t in key_tags if t in car.tags)
    if hit == 0:
        return PURPOSE_SCORE * 0.4, f"与「{q.purpose.value}」场景匹配一般"
    ratio = hit / len(key_tags)
    return PURPOSE_SCORE * (0.6 + 0.4 * ratio), f"契合「{q.purpose.value}」场景（命中 {hit}/{len(key_tags)}）"


def _score_brand(car: Car, q: Questionnaire) -> tuple[float, str]:
    """品牌偏好得分。"""
    if not q.brand_preferences:
        return BRAND_SCORE, "未限定品牌"
    if car.brand in q.brand_preferences:
        return BRAND_SCORE, f"品牌 {car.brand} 在偏好列表中"
    return BRAND_SCORE * 0.5, f"品牌 {car.brand} 不在偏好列表"


def _score_priority(car: Car, q: Questionnaire) -> tuple[float, str]:
    """优先级维度得分：检查该维度的关键参数/标签是否突出。"""
    key_specs = PRIORITY_SPECS.get(q.priority, [])
    if not key_specs:
        return PRIORITY_SCORE, "综合均衡"
    specs_text = " ".join(str(v) for v in car.specs.values()) + " " + " ".join(car.tags)
    hit = sum(1 for k in key_specs if k in specs_text)
    if hit == 0:
        return PRIORITY_SCORE * 0.4, f"「{q.priority.value}」方面表现一般"
    return PRIORITY_SCORE * (0.7 + 0.3 * hit / len(key_specs)), f"在「{q.priority.value}」维度有亮点"


def score_car(car: Car, q: Questionnaire) -> RecommendationResult:
    """对单辆车按问卷打分，返回结果与理由。"""
    reasons: list[str] = []
    total = 0.0
    for scorer in (_score_price, _score_energy, _score_seats, _score_purpose, _score_brand, _score_priority):
        score, reason = scorer(car, q)
        total += score
        reasons.append(reason)
    # 归一化到 0-100
    max_total = PRICE_SCORE + ENERGY_SCORE + SEATS_SCORE + PURPOSE_SCORE + BRAND_SCORE + PRIORITY_SCORE
    normalized = round(total / max_total * 100, 1)
    return RecommendationResult(car=car, score=normalized, reasons=reasons)


def recommend(cars: list[Car], q: Questionnaire, top_n: int = 5) -> list[RecommendationResult]:
    """对所有车型打分，按分数降序返回 Top-N 推荐。"""
    results = [score_car(car, q) for car in cars]
    results.sort(key=lambda r: r.score, reverse=True)
    return results[:top_n]
