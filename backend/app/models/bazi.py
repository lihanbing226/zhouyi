"""八字命盘数据模型"""
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base


class BaziRecord(Base):
    """八字命盘记录表"""

    __tablename__ = "bazi_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)

    # 出生信息
    birth_datetime: Mapped[datetime] = mapped_column(DateTime)  # 出生时间
    birth_gender: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # 'M' | 'F'
    birth_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # 出生地点

    # 四柱天干地支（如 "甲" 和 "子"）
    year_gan: Mapped[str] = mapped_column(String(1))  # 年干
    year_zhi: Mapped[str] = mapped_column(String(1))  # 年支
    month_gan: Mapped[str] = mapped_column(String(1))  # 月干
    month_zhi: Mapped[str] = mapped_column(String(1))  # 月支
    day_gan: Mapped[str] = mapped_column(String(1))  # 日干（日主）
    day_zhi: Mapped[str] = mapped_column(String(1))  # 日支
    hour_gan: Mapped[str] = mapped_column(String(1))  # 时干
    hour_zhi: Mapped[str] = mapped_column(String(1))  # 时支

    # 五行统计 JSON: {"金": 2, "木": 1, "水": 0, "火": 2, "土": 0}
    wuxing_score: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # 日主强弱判断
    day_master: Mapped[Optional[str]] = mapped_column(String(1), nullable=True)  # 日主天干
    strength: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # '身强' | '身弱'

    # 命局分析
    analysis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    luck_outlook: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # 运势展望

    # 大运信息（JSON 数组，包含每个大运的起止年份和天干地支）
    dayun: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<BaziRecord(id={self.id}, user_id={self.user_id})>"
