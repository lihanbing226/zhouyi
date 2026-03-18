"""统一历史记录 API 的 Pydantic schema"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HistoryListItem(BaseModel):
    """统一历史记录项"""

    id: str
    type: Literal["divination", "bazi"]
    title: str
    summary: str
    detail: str | None = None
    created_at: datetime


class HistoryListResponse(BaseModel):
    """统一历史记录列表响应"""

    items: list[HistoryListItem]
    total: int
    page: int
    page_size: int
    total_pages: int
