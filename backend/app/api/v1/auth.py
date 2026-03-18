"""用户认证 API 路由"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.core.database import get_db
from backend.app.core.security import hash_password, verify_password, create_access_token, verify_token
from backend.app.api.deps import get_current_user
from backend.app.models.user import User
from backend.app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserInfoResponse,
)

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=UserInfoResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """注册新用户。

    用户名唯一，密码使用 bcrypt 加密存储。
    """
    # 检查用户名是否已存在
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="用户名已存在",
        )

    # 检查邮箱唯一性（如果提供了邮箱）
    if request.email:
        result = await db.execute(select(User).where(User.email == request.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="邮箱已被注册",
            )

    # 创建用户
    user = User(
        username=request.username,
        hashed_password=hash_password(request.password),
        email=request.email,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserInfoResponse(id=user.id, username=user.username, email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """用户登录，返回 JWT access token。"""
    # 查找用户
    result = await db.execute(select(User).where(User.username == request.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )

    # 生成 token
    token = create_access_token(data={"sub": user.id})

    return TokenResponse(access_token=token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """刷新 JWT token。

    需要提供有效的旧 token（在 Authorization header 中）。
    """
    new_token = create_access_token(data={"sub": current_user.id})
    return TokenResponse(access_token=new_token)


@router.get("/me", response_model=UserInfoResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """获取当前用户信息。"""
    return UserInfoResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
    )
