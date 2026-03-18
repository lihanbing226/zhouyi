"""八字计算和历史记录 API 路由"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.bazi import BaziRecord
from backend.app.schemas.bazi import (
    BaziCalculateRequest,
    BaziCalculateResponse,
    BaziHistoryItem,
)
from backend.app.services.bazi.analyzer import analyze_bazi

router = APIRouter(prefix="/bazi", tags=["八字"])


@router.post("/calculate", response_model=BaziCalculateResponse)
async def calculate(
    request: BaziCalculateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """计算八字命盘。

    需要 JWT 鉴权。结果自动保存到历史记录。
    """
    # 执行八字分析
    result = analyze_bazi(request.birth_datetime, gender=request.gender)

    # 创建记录
    record_id = str(uuid.uuid4())
    record = BaziRecord(
        id=record_id,
        user_id=current_user.id,
        birth_datetime=request.birth_datetime,
        birth_gender=request.gender,
        birth_location=request.location,
        year_gan=result["year_gan"],
        year_zhi=result["year_zhi"],
        month_gan=result["month_gan"],
        month_zhi=result["month_zhi"],
        day_gan=result["day_gan"],
        day_zhi=result["day_zhi"],
        hour_gan=result["hour_gan"],
        hour_zhi=result["hour_zhi"],
        day_master=result["day_master"],
        strength=result["strength"],
        wuxing_score=result["wuxing_score"],
        analysis=result["analysis"],
        luck_outlook=result["luck_outlook"],
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return BaziCalculateResponse(
        id=record.id,
        year_gan=record.year_gan,
        year_zhi=record.year_zhi,
        month_gan=record.month_gan,
        month_zhi=record.month_zhi,
        day_gan=record.day_gan,
        day_zhi=record.day_zhi,
        hour_gan=record.hour_gan,
        hour_zhi=record.hour_zhi,
        day_master=record.day_master,
        strength=record.strength,
        wuxing_score=record.wuxing_score,
        analysis=record.analysis,
        luck_outlook=record.luck_outlook,
    )


@router.get("/records/{record_id}", response_model=BaziCalculateResponse)
async def get_record(
    record_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询单个八字命盘记录。

    需要 JWT 鉴权，只能查询自己的记录。
    """
    result = await db.execute(
        select(BaziRecord).where(
            BaziRecord.id == record_id,
            BaziRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在",
        )

    return BaziCalculateResponse(
        id=record.id,
        year_gan=record.year_gan,
        year_zhi=record.year_zhi,
        month_gan=record.month_gan,
        month_zhi=record.month_zhi,
        day_gan=record.day_gan,
        day_zhi=record.day_zhi,
        hour_gan=record.hour_gan,
        hour_zhi=record.hour_zhi,
        day_master=record.day_master,
        strength=record.strength,
        wuxing_score=record.wuxing_score,
        analysis=record.analysis,
        luck_outlook=record.luck_outlook,
    )


@router.get("/history", response_model=list[BaziHistoryItem])
async def get_bazi_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """查询当前用户的八字历史记录。

    需要 JWT 鉴权。按时间倒序排列。
    """
    offset = (page - 1) * page_size
    stmt = (
        select(BaziRecord)
        .where(BaziRecord.user_id == current_user.id)
        .order_by(BaziRecord.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        BaziHistoryItem(
            id=r.id,
            birth_datetime=r.birth_datetime,
            day_master=r.day_master,
            strength=r.strength,
            created_at=r.created_at,
        )
        for r in records
    ]
