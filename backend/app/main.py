"""FastAPI 主应用程序入口"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import engine, Base
from backend.app.models import User, DivinationRecord, BaziRecord  # noqa: F401 确保模型注册


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时创建数据库表。"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="周易算命网站 - 智能卜卦 + 八字命盘 + 数据看板",
    lifespan=lifespan,
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 健康检查端点
@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    return {"status": "ok"}


@app.get("/", tags=["Root"])
async def root():
    """根路由"""
    return {"message": f"欢迎来到 {settings.APP_NAME}", "version": settings.APP_VERSION}


# API 路由注册
from backend.app.api.v1.router import api_router

app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
