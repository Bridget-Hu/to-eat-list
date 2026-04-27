# routes_health.py

#健康检查接口
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/ping")
def ping():
    return {"message": "pong"}