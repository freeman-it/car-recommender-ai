"""应用配置：从环境变量 / .env 文件读取。"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """全局配置。可通过环境变量或 .env 覆盖。"""

    app_name: str = "Car Recommender AI"
    debug: bool = True
    # 车型库路径（相对项目根目录）
    data_path: str = "app/data/cars.json"

    # 可选 LLM 配置（OpenAI 兼容接口）
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
