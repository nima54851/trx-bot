"""
订单API路由
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    OrderCreateRequest, OrderCreateResponse,
    OrderDetailResponse
)
from services import lease_service
from models import Order

router = APIRouter()


@router.post("/create", response_model=OrderCreateResponse)
async def create_order(req: OrderCreateRequest, db: Session = Depends(get_db)):
    """创建租赁订单"""
    try:
        order = lease_service.create_lease_order(
            db=db,
            user_id=req.user_id,
            trx_address=req.trx_address,
            energy_amount=req.energy_amount,
            rent_days=req.rent_days,
            username=req.username,
        )
        return OrderCreateResponse(
            order_id=order.order_id,
            deposit_address=order.deposit_address,
            trx_amount=order.trx_amount,
            status=order.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(order_id: str, db: Session = Depends(get_db)):
    """查询订单详情"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.get("/user/{user_id}")
async def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """获取用户所有订单"""
    orders = lease_service.get_user_orders(db, user_id)
    return {"total": len(orders), "orders": orders}


@router.post("/{order_id}/confirm")
async def confirm_payment(order_id: str, txid: str, db: Session = Depends(get_db)):
    """确认支付（Webhook回调）"""
    try:
        order = lease_service.confirm_payment(db, order_id, txid)
        return {"success": True, "status": order.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
