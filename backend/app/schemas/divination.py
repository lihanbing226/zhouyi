"""卜卦 API 的 Pydantic schema"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class DivinationCastRequest(BaseModel):
    """卜卦请求"""
    question: str = Field(..., min_length=1, max_length=200, description="占卜问题")
    method: str = Field(default="coins", description="卜卦方法：coins | yarrow")
    yao_sequence: str | None = Field(
        default=None,
        pattern=r"^[6789]{6}$",
        description="可选的六爻序列，如'679867'；传入后端将按该序列解卦",
    )


class DivinationCastResponse(BaseModel):
    """卜卦响应"""
    id: str
    hexagram_num: int = Field(..., ge=1, le=64)
    hexagram_name: str
    yao_sequence: str = Field(..., description="爻序列，如'679867'")
    changing_yao: Optional[List[int]] = Field(None, description="变爻位置数组")
    changed_hex_num: Optional[int] = None
    changed_hex_name: Optional[str] = None
    luck_score: int = Field(..., ge=1, le=100)
    interpretation: str


class HexagramInfo(BaseModel):
    """单个卦象的完整信息"""
    num: int = Field(..., ge=1, le=64)
    name: str
    symbol: str = Field(..., description="八卦符号，如 ☰")
    trigram_upper: str = Field(..., description="上卦")
    trigram_lower: str = Field(..., description="下卦")
    meaning: str = Field(..., description="卦象含义")
    image: str = Field(..., description="卦象解释")
    judgement: str = Field(..., description="彖辞")
    yao_texts: List[str] = Field(..., description="六爻爻辞")


class HexagramListResponse(BaseModel):
    """卦象列表"""
    total: int
    hexagrams: List[HexagramInfo]


class DivinationHistoryItem(BaseModel):
    """历史记录项"""
    id: str
    question: str
    hexagram_name: str
    luck_score: int
    created_at: datetime

    class Config:
        from_attributes = True
