"""车型与推荐结果模型。"""
from typing import Any

from pydantic import BaseModel, Field


class Car(BaseModel):
    """车型样本。"""

    id: str = Field(..., description="唯一标识")
    brand: str = Field(..., description="品牌")
    name: str = Field(..., description="车型名称")
    price: float = Field(..., ge=0, description="指导价（万元）")
    energy_type: str = Field(..., description="能源类型：燃油/混动/纯电")
    seats: int = Field(5, ge=2, le=9, description="座位数")
    segment: str = Field(..., description="级别：轿车/SUV/MPV/跑车")
    tags: list[str] = Field(default_factory=list, description="特性标签")
    specs: dict[str, Any] = Field(default_factory=dict, description="关键参数")


class RecommendationResult(BaseModel):
    """单条推荐结果。"""

    car: Car
    score: float = Field(..., description="综合匹配分（0-100）")
    reasons: list[str] = Field(default_factory=list, description="推荐理由")
