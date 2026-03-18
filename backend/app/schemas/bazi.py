"""八字命盘 API 的 Pydantic schema"""
from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class BaziCalculateRequest(BaseModel):
    """八字计算请求"""
    birth_datetime: datetime = Field(..., description="出生时间")
    gender: Optional[str] = Field(None, description="性别：M | F")
    location: Optional[str] = Field(None, description="出生地点")


class WuxingScore(BaseModel):
    """五行评分"""
    jin: int = Field(default=0, description="金")
    mu: int = Field(default=0, description="木")
    shui: int = Field(default=0, description="水")
    huo: int = Field(default=0, description="火")
    tu: int = Field(default=0, description="土")


class BaziPillar(BaseModel):
    """四柱单个柱子"""
    gan: str = Field(..., description="天干")
    zhi: str = Field(..., description="地支")
    wuxing: str = Field(..., description="五行")


class BaziCalculateResponse(BaseModel):
    """八字计算响应"""
    id: str
    year_gan: str
    year_zhi: str
    month_gan: str
    month_zhi: str
    day_gan: str
    day_zhi: str
    hour_gan: str
    hour_zhi: str
    day_master: str = Field(..., description="日主天干")
    strength: str = Field(..., description="身强 | 身弱")
    wuxing_score: Dict[str, int]
    analysis: str
    luck_outlook: str


class BaziHistoryItem(BaseModel):
    """八字历史记录"""
    id: str
    birth_datetime: datetime
    day_master: str
    strength: str
    created_at: datetime

    class Config:
        from_attributes = True
