"""通用历史记录 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.divination import DivinationRecord
from backend.app.models.bazi import BaziRecord
from backend.app.schemas.history import HistoryListItem, HistoryListResponse

router = APIRouter(prefix="/history", tags=["历史记录"])


def _format_datetime(dt) -> str:
    """格式化时间文本。"""
    return dt.strftime("%Y-%m-%d %H:%M")


@router.get("", response_model=HistoryListResponse)
async def list_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    sort: str = Query("newest", description="排序方式：newest | oldest"),
    record_type: str = Query("all", alias="type", description="记录类型：all | divination | bazi"),
):
    """查询当前用户的统一历史记录列表。"""
    if sort not in {"newest", "oldest"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort 必须为 'newest' 或 'oldest'",
        )

    if record_type not in {"all", "divination", "bazi"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="type 必须为 'all'、'divination' 或 'bazi'",
        )

    items: list[HistoryListItem] = []

    if record_type in {"all", "divination"}:
        result = await db.execute(
            select(DivinationRecord).where(DivinationRecord.user_id == current_user.id)
        )
        divination_records = result.scalars().all()
        items.extend(
            HistoryListItem(
                id=record.id,
                type="divination",
                title=record.hexagram_name,
                summary=f"所问：{record.question}｜运势评分：{record.luck_score}",
                detail=f"问题：{record.question}",
                created_at=record.created_at,
            )
            for record in divination_records
        )

    if record_type in {"all", "bazi"}:
        result = await db.execute(
            select(BaziRecord).where(BaziRecord.user_id == current_user.id)
        )
        bazi_records = result.scalars().all()
        items.extend(
            HistoryListItem(
                id=record.id,
                type="bazi",
                title=f"{record.day_master}日主",
                summary=(
                    f"出生时间：{_format_datetime(record.birth_datetime)}｜命局：{record.strength}"
                ),
                detail=f"日主：{record.day_master}，命局判断：{record.strength}",
                created_at=record.created_at,
            )
            for record in bazi_records
        )

    reverse = sort == "newest"
    items.sort(key=lambda item: item.created_at, reverse=reverse)

    total = len(items)
    total_pages = max(1, (total + page_size - 1) // page_size)
    start = (page - 1) * page_size
    end = start + page_size

    return HistoryListResponse(
        items=items[start:end],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.delete("/{record_type}/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_type: str,
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除历史记录。

    Args:
        record_type: 记录类型，"divination" 或 "bazi"
        record_id: 记录 ID
    """
    if record_type == "divination":
        model = DivinationRecord
    elif record_type == "bazi":
        model = BaziRecord
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="record_type 必须为 'divination' 或 'bazi'",
        )

    result = await db.execute(
        select(model).where(model.id == record_id, model.user_id == current_user.id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在",
        )

    await db.delete(record)
    await db.commit()
