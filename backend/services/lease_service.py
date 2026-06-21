"""
租赁服务 — 核心业务逻辑
"""
import uuid
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Order, User, LeaseRecord
from config import settings
from services.tron_service import tron_service


def generate_order_id() -> str:
    return f"LE{int(time.time() * 1000)}{uuid.uuid4().hex[:6].upper()}"


def calculate_price(energy_amount: int, rent_days: int) -> float:
    """计算应付金额：能量 * 天数 * 单价"""
    return round(energy_amount * rent_days * settings.ENERGY_PRICE_PER_DAY / 1000, 4)


def get_or_create_user(db: Session, user_id: int, username: str = None) -> User:
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        user = User(user_id=user_id, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_lease_order(
    db: Session,
    user_id: int,
    trx_address: str,
    energy_amount: int,
    rent_days: int,
    username: str = None
) -> Order:
    """创建租赁订单"""
    # 验证地址
    if not tron_service.validate_address(trx_address):
        raise ValueError("无效的TRX地址")

    # 检查能量范围
    if energy_amount < settings.MIN_ENERGY or energy_amount > settings.MAX_ENERGY:
        raise ValueError(f"能量范围: {settings.MIN_ENERGY} ~ {settings.MAX_ENERGY}")

    if rent_days < settings.MIN_RENT_DAYS or rent_days > settings.MAX_RENT_DAYS:
        raise ValueError(f"租用天数: {settings.MIN_RENT_DAYS} ~ {settings.MAX_RENT_DAYS}")

    # 生成唯一支付地址（示例：使用订单号作为标识）
    deposit_address = settings.TRON_WALLET_ADDRESS
    trx_amount = calculate_price(energy_amount, rent_days)

    order = Order(
        order_id=generate_order_id(),
        user_id=user_id,
        trx_address=trx_address,
        energy_amount=energy_amount,
        rent_days=rent_days,
        trx_amount=trx_amount,
        deposit_address=deposit_address,
        status="pending",
    )
    db.add(order)

    # 更新用户统计
    user = get_or_create_user(db, user_id, username)
    user.total_orders += 1

    db.commit()
    db.refresh(order)
    return order


def confirm_payment(db: Session, order_id: str, txid: str) -> Order:
    """确认支付，触发租赁"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise ValueError("订单不存在")

    if order.status != "pending":
        raise ValueError(f"订单状态异常: {order.status}")

    # 更新订单状态
    order.status = "paid"
    order.deposit_txid = txid
    order.lease_start = datetime.utcnow()
    order.lease_end = order.lease_start + timedelta(days=order.rent_days)

    # 更新用户消费
    user = db.query(User).filter(User.user_id == order.user_id).first()
    if user:
        user.total_spent += order.trx_amount

    db.commit()
    db.refresh(order)

    # 记录租赁动作
    record = LeaseRecord(
        order_id=order_id,
        action="paid_confirmed",
        result=f"支付确认，金额: {order.trx_amount} TRX"
    )
    db.add(record)
    db.commit()

    return order


def expire_order(db: Session, order_id: str) -> Order:
    """过期订单（租期结束）"""
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order or order.status != "rented":
        return order

    order.status = "expired"
    db.commit()
    db.refresh(order)

    record = LeaseRecord(
        order_id=order_id,
        action="expired",
        result="租期结束，订单过期"
    )
    db.add(record)
    db.commit()

    return order


def get_user_orders(db: Session, user_id: int) -> list[Order]:
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.created_at.desc()).all()


def get_all_orders(db: Session, skip: int = 0, limit: int = 50, status: str = None) -> list[Order]:
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    return query.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def count_orders(db: Session, status: str = None) -> int:
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    return query.count()
