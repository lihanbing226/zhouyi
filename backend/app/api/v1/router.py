"""API v1 路由聚合"""

from fastapi import APIRouter

from backend.app.api.v1.auth import router as auth_router
from backend.app.api.v1.bazi import router as bazi_router
from backend.app.api.v1.dashboard import router as dashboard_router
from backend.app.api.v1.divination import router as divination_router
from backend.app.api.v1.history import router as history_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(bazi_router)
api_router.include_router(dashboard_router)
api_router.include_router(divination_router)
api_router.include_router(history_router)
