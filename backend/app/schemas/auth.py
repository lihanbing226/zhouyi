"""用户认证 API 的 Pydantic schema"""

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    email: str | None = Field(None, max_length=100, description="邮箱（可选）")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: str
    username: str
    email: str | None = None

    class Config:
        from_attributes = True
