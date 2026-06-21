"""
Pydantic 请求/响应模型
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# === 订单 ===
class OrderCreateRequest(BaseModel):
    user_id: int
    trx_address: str = Field(..., min_length=34, max_length=34)
    energy_amount: int = Field(..., ge=5000, le=500000)
    rent_days: int = Field(..., ge=1, le=30)
    username: Optional[str] = None


class OrderCreateResponse(BaseModel):
    order_id: str
    deposit_address: str
    trx_amount: float
    qr_code_data: Optional[str] = None
    status: str


class OrderDetailResponse(BaseModel):
    order_id: str
    status: str
    energy_amount: int
    rent_days: int
    trx_amount: float
    deposit_address: str
    deposit_txid: Optional[str] = None
    lease_start: Optional[datetime] = None
    lease_end: Optional[datetime] = None
    created_at: datetime


# === 能量查询 ===
class EnergyPriceRequest(BaseModel):
    energy_amount: int
    rent_days: int


class EnergyPriceResponse(BaseModel):
    energy_amount: int
    rent_days: int
    trx_amount: float
    energy_price_per_day: float


class EnergyQuoteResponse(BaseModel):
    # 能量定价表
    prices: list[dict]


# === 管理 ===
class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    username: str


class DashboardStatsResponse(BaseModel):
    total_orders: int
    total_revenue: float
    active_leases: int
    pending_orders: int
    today_orders: int
    today_revenue: float


class OrderListResponse(BaseModel):
    total: int
    orders: list[OrderDetailResponse]
