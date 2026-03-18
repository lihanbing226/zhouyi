"""异步数据库连接和会话管理"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from backend.app.core.config import settings

# 创建异步数据库引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",  # 开发环境输出 SQL
    future=True,
)

# 异步会话工厂
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# ORM 基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """
    FastAPI 依赖注入：获取数据库会话
    用法：
        async def my_endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
