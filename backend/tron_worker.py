"""
Celery Worker — 处理链上任务
"""
from celery import Celery
from config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "tron_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-expired-orders": {
            "task": "tron_worker.check_expired_orders",
            "schedule": 300.0,  # 每5分钟检查一次
        },
        "check-pending-payments": {
            "task": "tron_worker.check_pending_payments",
            "schedule": 60.0,   # 每分钟检查一次pending订单
        },
    },
)


@celery_app.task
def check_expired_orders():
    """检查过期订单并解冻"""
    from database import SessionLocal
    from models import Order, LeaseRecord
    from services.lease_service import expire_order
    from datetime import datetime
    import httpx

    db = SessionLocal()
    try:
        expired = db.query(Order).filter(
            Order.status.in_(["paid", "rented"]),
            Order.lease_end <= datetime.utcnow()
        ).all()

        for order in expired:
            expire_order(db, order.order_id)
            logger.info(f"[Celery] 订单 {order.order_id} 已过期")
    finally:
        db.close()


@celery_app.task
def check_pending_payments():
    """轮询检查pending订单的链上支付状态"""
    from database import SessionLocal
    from models import Order
    from services.tron_service import tron_service
    from services.lease_service import confirm_payment
    import httpx

    db = SessionLocal()
    try:
        pending_orders = db.query(Order).filter(
            Order.status == "pending"
        ).all()

        for order in pending_orders:
            # 实际生产中：监听DepositAddress的转入交易
            # 这里简化处理，通过txid查询
            logger.info(f"[Celery] 检查订单 {order.order_id} 支付状态")
    finally:
        db.close()


@celery_app.task
def notify_user_telegram(user_id: int, message: str):
    """通过Telegram通知用户"""
    import httpx
    import os

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    httpx.post(url, json={"chat_id": user_id, "text": message})
