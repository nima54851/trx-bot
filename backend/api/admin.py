"""
管理API路由
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from schemas import (
    AdminLoginRequest, AdminLoginResponse,
    DashboardStatsResponse, OrderListResponse, OrderDetailResponse
)
from models import Order, User, SystemConfig
from services import lease_service
from config import settings
import hashlib
import time

router = APIRouter()

# 简单的Token管理（生产环境请用JWT）
_active_tokens = {}


def verify_token(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未授权")
    token = authorization.replace("Bearer ", "")
    if token not in _active_tokens:
        raise HTTPException(status_code=401, detail="Token无效")
    if _active_tokens[token]["expire"] < time.time():
        del _active_tokens[token]
        raise HTTPException(status_code=401, detail="Token已过期")
    return token


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(req: AdminLoginRequest):
    """管理员登录"""
    if req.username != settings.ADMIN_USERNAME or req.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    token = hashlib.sha256(f"{req.username}{time.time()}".encode()).hexdigest()
    _active_tokens[token] = {
        "username": req.username,
        "expire": time.time() + 86400 * 7,
    }
    return AdminLoginResponse(token=token, username=req.username)


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """获取仪表盘统计数据"""
    verify_token(authorization)

    total_orders = db.query(func.count(Order.id)).scalar()
    total_revenue = db.query(func.sum(Order.trx_amount)).filter(
        Order.status.in_(["paid", "rented", "expired"])
    ).scalar() or 0.0

    active_leases = db.query(func.count(Order.id)).filter(
        Order.status.in_(["paid", "rented"])
    ).scalar()

    pending_orders = db.query(func.count(Order.id)).filter(
        Order.status == "pending"
    ).scalar()

    from datetime import datetime, timedelta
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_orders = db.query(func.count(Order.id)).filter(
        Order.created_at >= today_start
    ).scalar()

    today_revenue = db.query(func.sum(Order.trx_amount)).filter(
        Order.status.in_(["paid", "rented"]),
        Order.created_at >= today_start
    ).scalar() or 0.0

    return DashboardStatsResponse(
        total_orders=total_orders,
        total_revenue=round(total_revenue, 4),
        active_leases=active_leases,
        pending_orders=pending_orders,
        today_orders=today_orders,
        today_revenue=round(today_revenue, 4),
    )


@router.get("/orders", response_model=OrderListResponse)
async def list_orders(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """订单列表"""
    verify_token(authorization)
    orders = lease_service.get_all_orders(db, skip, limit, status)
    total = lease_service.count_orders(db, status)
    return OrderListResponse(total=total, orders=orders)


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 20,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """用户列表"""
    verify_token(authorization)
    users = db.query(User).offset(skip).limit(limit).all()
    total = db.query(func.count(User.id)).scalar()
    return {"total": total, "users": users}
