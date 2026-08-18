"""购车问卷数据模型。"""
from enum import Enum

from pydantic import BaseModel, Field, model_validator


class EnergyType(str, Enum):
    """能源类型。"""

    FUEL = "燃油"
    HYBRID = "混动"
    EV = "纯电"


class Purpose(str, Enum):
    """主要用车场景。"""

    COMMUTE = "通勤代步"
    FAMILY = "家庭用车"
    BUSINESS = "商务出行"
    SPORT = "运动操控"
    OFFROAD = "越野旅行"


class Priority(str, Enum):
    """最看重的维度。"""

    SPACE = "空间"
    POWER = "动力"
    ECONOMY = "经济性"
    TECH = "智能科技"
    SAFETY = "安全"
    VALUE = "保值率"
    BALANCED = "综合"


class Questionnaire(BaseModel):
    """用户提交的购车问卷。"""

    budget_min: float = Field(..., ge=0, description="预算下限（万元）")
    budget_max: float = Field(..., gt=0, description="预算上限（万元）")
    energy_type: list[EnergyType] = Field(
        default_factory=list, description="可接受的能源类型，空表示不限"
    )
    purpose: Purpose = Field(..., description="主要用车场景")
    seats: int = Field(5, ge=2, le=9, description="所需座位数")
    brand_preferences: list[str] = Field(
        default_factory=list, description="偏好品牌，如 ['比亚迪', '丰田']"
    )
    priority: Priority = Field(Priority.BALANCED, description="最看重的维度")

    @model_validator(mode="after")
    def _check_budget(self) -> "Questionnaire":
        if self.budget_max <= self.budget_min:
            raise ValueError("budget_max 必须大于 budget_min")
        return self

    @property
    def budget_mid(self) -> float:
        return (self.budget_min + self.budget_max) / 2

    @property
    def budget_span(self) -> float:
        return max(self.budget_max - self.budget_min, 0.01)
