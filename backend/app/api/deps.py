"""FastAPI 依赖注入"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import verify_token
from backend.app.models.user import User
from sqlalchemy import select

http_bearer = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    验证 JWT token 并返回当前用户
    用法：
        async def protected_endpoint(current_user: User = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials
    user_id = verify_token(token)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭证",
            headers={"WWW-Authenticate": "Bearer"},
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer)
    if http_bearer else None,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    可选的用户验证（不验证则返回 None）
    """
    if not credentials:
        return None

    token = credentials.credentials
    user_id = verify_token(token)

    if not user_id:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
