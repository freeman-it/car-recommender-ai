"""可选 LLM 增强：调用 OpenAI 兼容接口生成个性化推荐说明。"""
from app.config import settings
from app.models.questionnaire import Questionnaire
from app.models.recommendation import RecommendationResult

_SYSTEM_PROMPT = (
    "你是一位专业的汽车购车顾问。请根据用户问卷与候选车型的评分结果，"
    "用简洁通俗的中文生成一段不超过 150 字的个性化购车建议，"
    "说明推荐理由与选车要点，不要逐条复述数据。"
)


def llm_available() -> bool:
    """是否配置了 LLM 服务。"""
    return bool(settings.llm_api_key and settings.llm_base_url)


def _build_user_prompt(q: Questionnaire, results: list[RecommendationResult]) -> str:
    car_lines = "\n".join(
        f"- {r.car.brand} {r.car.name}（{r.car.price:.1f}万，{r.car.energy_type}，"
        f"{r.car.seats}座）综合分 {r.score}"
        for r in results
    )
    return (
        f"问卷：预算 {q.budget_min:.0f}-{q.budget_max:.0f} 万元，能源 {[e.value for e in q.energy_type]}，"
        f"场景「{q.purpose.value}」，{q.seats} 座，偏好品牌 {q.brand_preferences}，"
        f"最看重「{q.priority.value}」。\n\n候选车型评分：\n{car_lines}\n\n请给出购车建议。"
    )


async def generate_advice(
    q: Questionnaire, results: list[RecommendationResult]
) -> str | None:
    """生成个性化建议。未配置 LLM 时返回 None。"""
    if not llm_available():
        return None

    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        resp = await client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(q, results)},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        return resp.choices[0].message.content
    except Exception as exc:  # 不因 LLM 故障影响主流程
        return f"（AI 建议生成失败：{exc}）"
