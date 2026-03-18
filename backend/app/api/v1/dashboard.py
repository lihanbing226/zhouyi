"""数据看板 API 路由

提供数据聚合接口供前端 ECharts 图表渲染。
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.app.core.database import get_db
from backend.app.models.divination import DivinationRecord
from backend.app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["数据看板"])


@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
):
    """概览数据：今日卜卦数、活跃用户数、平均运势评分、趋势。

    无需鉴权（公开看板）。
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - timedelta(days=1)

    # 今日卜卦数
    today_count_result = await db.execute(
        select(func.count(DivinationRecord.id)).where(
            DivinationRecord.created_at >= today_start
        )
    )
    today_count = today_count_result.scalar() or 0

    # 昨日卜卦数（用于计算趋势）
    yesterday_count_result = await db.execute(
        select(func.count(DivinationRecord.id)).where(
            DivinationRecord.created_at >= yesterday_start,
            DivinationRecord.created_at < today_start,
        )
    )
    yesterday_count = yesterday_count_result.scalar() or 0

    # 趋势百分比
    if yesterday_count > 0:
        trend = round((today_count - yesterday_count) / yesterday_count * 100, 1)
    elif today_count > 0:
        trend = 100.0
    else:
        trend = 0.0

    # 今日活跃用户数（去重）
    active_users_result = await db.execute(
        select(func.count(func.distinct(DivinationRecord.user_id))).where(
            DivinationRecord.created_at >= today_start
        )
    )
    active_users = active_users_result.scalar() or 0

    # 平均运势评分
    avg_score_result = await db.execute(
        select(func.avg(DivinationRecord.luck_score))
    )
    avg_luck_score = avg_score_result.scalar()
    avg_luck_score = round(float(avg_luck_score), 1) if avg_luck_score else 50.0

    # 总卜卦数
    total_count_result = await db.execute(
        select(func.count(DivinationRecord.id))
    )
    total_count = total_count_result.scalar() or 0

    return {
        "today_count": today_count,
        "active_users": active_users,
        "avg_luck_score": avg_luck_score,
        "trend": trend,
        "total_count": total_count,
    }


@router.get("/hexagram-stats")
async def get_hexagram_stats(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="统计天数范围"),
):
    """六十四卦频率统计。

    返回格式适配 ECharts 柱状图/饼图。
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # 按卦号分组统计
    stmt = (
        select(
            DivinationRecord.hexagram_num,
            DivinationRecord.hexagram_name,
            func.count(DivinationRecord.id).label("count"),
        )
        .where(DivinationRecord.created_at >= since)
        .group_by(DivinationRecord.hexagram_num, DivinationRecord.hexagram_name)
        .order_by(func.count(DivinationRecord.id).desc())
    )
    result = await db.execute(stmt)
    rows = result.all()

    return [
        {"num": row.hexagram_num, "name": row.hexagram_name, "count": row.count}
        for row in rows
    ]


@router.get("/user-trend")
async def get_user_trend(
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=90, description="趋势天数"),
):
    """用户活跃趋势（每日卜卦次数）。

    返回格式适配 ECharts 折线图。
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # SQLite 在 CAST(datetime AS DATE) 场景下可能返回非字符串对象，导致 ORM 结果处理报错。
    # 这里直接取 created_at 后在 Python 侧按日期聚合，确保 SQLite / PostgreSQL 行为一致。
    stmt = select(DivinationRecord.created_at).where(DivinationRecord.created_at >= since)
    result = await db.execute(stmt)
    timestamps = result.scalars().all()

    # 填充缺失的日期（确保连续日期）
    date_counts: dict[str, int] = {}
    for created_at in timestamps:
        date_key = created_at.strftime("%Y-%m-%d")
        date_counts[date_key] = date_counts.get(date_key, 0) + 1

    trend_data = []
    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        trend_data.append({
            "date": date,
            "count": date_counts.get(date, 0),
        })

    return trend_data


@router.get("/luck-distribution")
async def get_luck_distribution(
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, ge=1, le=365, description="统计天数范围"),
):
    """运势评分分布（适配 ECharts 直方图）。

    将 1-100 分分为 5 个区间。
    """
    since = datetime.now(timezone.utc) - timedelta(days=days)

    # 查询所有运势评分
    stmt = (
        select(DivinationRecord.luck_score)
        .where(DivinationRecord.created_at >= since)
    )
    result = await db.execute(stmt)
    scores = [row[0] for row in result.all()]

    # 分区间统计
    bins = [
        {"label": "大凶 (1-20)", "min": 1, "max": 20, "count": 0},
        {"label": "小凶 (21-40)", "min": 21, "max": 40, "count": 0},
        {"label": "平 (41-60)", "min": 41, "max": 60, "count": 0},
        {"label": "吉 (61-80)", "min": 61, "max": 80, "count": 0},
        {"label": "大吉 (81-100)", "min": 81, "max": 100, "count": 0},
    ]

    for score in scores:
        for b in bins:
            if b["min"] <= score <= b["max"]:
                b["count"] += 1
                break

    return [{"label": b["label"], "count": b["count"]} for b in bins]
