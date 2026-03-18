"""环境变量配置（基于 pydantic-settings）"""
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用全局设置"""

    # 项目基本信息
    APP_NAME: str = "周易"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./zhou_yi.db"

    # JWT 鉴权
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # 生产环境必须更改
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Claude API（AI 解读）
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
