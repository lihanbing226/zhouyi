"""卜卦和卦象查询 API 路由"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.core.database import get_db
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.models.divination import DivinationRecord
from backend.app.schemas.divination import (
    DivinationCastRequest,
    DivinationCastResponse,
    HexagramInfo,
    HexagramListResponse,
    DivinationHistoryItem,
)
from backend.app.services.hexagram.hexagram_data import HEXAGRAMS, get_hexagram
from backend.app.services.hexagram.coins import cast_divination
from backend.app.services.hexagram.interpreter import interpret_hexagram

router = APIRouter(prefix="/divination", tags=["卜卦"])


@router.post("/cast", response_model=DivinationCastResponse)
async def cast(
    request: DivinationCastRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """执行一次卜卦，返回卦象和解读。

    需要 JWT 鉴权。卜卦结果自动保存到历史记录。
    """
    if request.method not in ("coins", "yarrow"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="method 必须为 'coins' 或 'yarrow'",
        )

    # 执行卜卦：若前端已完成投掷，则直接使用其上传的爻序列，保证展示与结果一致
    if request.yao_sequence:
        yao_seq = request.yao_sequence
    else:
        div_result = cast_divination()
        yao_seq = div_result["yao_sequence"]

    # 生成解读
    interp = interpret_hexagram(yao_seq, question=request.question)

    # 创建记录
    record_id = str(uuid.uuid4())
    record = DivinationRecord(
        id=record_id,
        user_id=current_user.id,
        question=request.question,
        method=request.method,
        yao_sequence=yao_seq,
        hexagram_num=interp["hexagram_num"],
        hexagram_name=interp["hexagram_name"],
        changing_yao=interp["changing_yao"],
        changed_hex_num=interp["changed_hex_num"],
        changed_hex_name=interp["changed_hex_name"],
        interpretation=interp["interpretation"],
        luck_score=interp["luck_score"],
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return DivinationCastResponse(
        id=record.id,
        hexagram_num=record.hexagram_num,
        hexagram_name=record.hexagram_name,
        yao_sequence=record.yao_sequence,
        changing_yao=record.changing_yao,
        changed_hex_num=record.changed_hex_num,
        changed_hex_name=record.changed_hex_name,
        luck_score=record.luck_score,
        interpretation=record.interpretation,
    )


@router.get("/hexagrams", response_model=HexagramListResponse)
async def list_hexagrams(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(64, ge=1, le=64, description="每页数量"),
):
    """查询所有六十四卦列表，支持分页。

    无需鉴权。
    """
    all_nums = sorted(HEXAGRAMS.keys())
    total = len(all_nums)
    start = (page - 1) * page_size
    end = start + page_size
    page_nums = all_nums[start:end]

    hexagrams = []
    for num in page_nums:
        data = HEXAGRAMS[num]
        hexagrams.append(HexagramInfo(
            num=data["num"],
            name=data["name"],
            symbol=data["symbol"],
            trigram_upper=data["trigram_upper"],
            trigram_lower=data["trigram_lower"],
            meaning=data["meaning"],
            image=data["image"],
            judgement=data["judgement"],
            yao_texts=data["yao_texts"],
        ))

    return HexagramListResponse(total=total, hexagrams=hexagrams)


@router.get("/hexagrams/{num}", response_model=HexagramInfo)
async def get_hexagram_detail(num: int):
    """查询单个卦象详情。

    无需鉴权。
    """
    if num < 1 or num > 64:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="卦号必须在 1-64 之间",
        )

    data = get_hexagram(num)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"卦号 {num} 不存在",
        )

    return HexagramInfo(
        num=data["num"],
        name=data["name"],
        symbol=data["symbol"],
        trigram_upper=data["trigram_upper"],
        trigram_lower=data["trigram_lower"],
        meaning=data["meaning"],
        image=data["image"],
        judgement=data["judgement"],
        yao_texts=data["yao_texts"],
    )


@router.get("/history", response_model=list[DivinationHistoryItem])
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """查询当前用户的卜卦历史记录。

    需要 JWT 鉴权。按时间倒序排列。
    """
    offset = (page - 1) * page_size
    stmt = (
        select(DivinationRecord)
        .where(DivinationRecord.user_id == current_user.id)
        .order_by(DivinationRecord.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        DivinationHistoryItem(
            id=r.id,
            question=r.question,
            hexagram_name=r.hexagram_name,
            luck_score=r.luck_score,
            created_at=r.created_at,
        )
        for r in records
    ]
