"""pytest 配置和共享 fixtures

提供测试数据库、异步客户端和认证 helper。
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from backend.app.core.database import Base, get_db
from backend.app.core.security import hash_password, create_access_token
from backend.app.main import app
from backend.app.models import User, DivinationRecord, BaziRecord


# 测试数据库：使用内存 SQLite
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话，每个测试用例独立建表和销毁。"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """创建测试 HTTP 客户端，注入测试数据库。"""

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """创建一个测试用户。"""
    user = User(
        username="testuser",
        hashed_password=hash_password("testpass123"),
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """生成测试用户的 JWT 认证头。"""
    token = create_access_token(data={"sub": test_user.id})
    return {"Authorization": f"Bearer {token}"}
