"""卜卦记录数据模型"""
from datetime import datetime
from typing import Optional
import uuid
import json

from sqlalchemy import String, DateTime, SmallInteger, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class DivinationRecord(Base):
    """卜卦记录表"""

    __tablename__ = "divination_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)

    # 卜卦信息
    question: Mapped[str] = mapped_column(Text)  # 占卜问题
    method: Mapped[str] = mapped_column(String(20))  # 'coins' | 'yarrow'

    # 爻序列（6位数字，如 '679867'，每位表示爻的阴阳类型）
    yao_sequence: Mapped[str] = mapped_column(String(6))

    # 本卦信息
    hexagram_num: Mapped[int] = mapped_column(SmallInteger)  # 1-64
    hexagram_name: Mapped[str] = mapped_column(String(20))  # 如 "乾卦"

    # 变爻信息（JSON 数组，如 [3, 5] 表示第3和第5爻变）
    changing_yao: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # 变卦信息
    changed_hex_num: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    changed_hex_name: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # 解读和评分
    interpretation: Mapped[str] = mapped_column(Text)  # 解读文本
    luck_score: Mapped[int] = mapped_column(SmallInteger, default=50)  # 1-100 的运势评分

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DivinationRecord(id={self.id}, user_id={self.user_id}, hexagram={self.hexagram_name})>"
