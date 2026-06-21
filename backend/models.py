"""
SQLAlchemy 数据模型
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, BigInteger
from sqlalchemy.sql import func
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), unique=True, index=True)        # 订单号
    user_id = Column(BigInteger, index=True)                     # Telegram用户ID
    trx_address = Column(String(64))                               # 用户TRX地址
    energy_amount = Column(Integer)                               # 能量数量
    rent_days = Column(Integer)                                   # 租用天数
    trx_amount = Column(Float)                                    # 应付TRX金额
    status = Column(String(32), default="pending")               # pending/paid/rented/expired/cancelled
    deposit_address = Column(String(64))                          # 支付地址
    deposit_txid = Column(String(128))                            # 链上交易hash
    lease_start = Column(DateTime, nullable=True)                 # 租赁开始时间
    lease_end = Column(DateTime, nullable=True)                   # 租赁结束时间
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True)
    username = Column(String(128), nullable=True)
    trx_address = Column(String(64), nullable=True)
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(64), unique=True, index=True)
    value = Column(Text)
    description = Column(String(256), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class LeaseRecord(Base):
    __tablename__ = "lease_records"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), index=True)
    action = Column(String(32))                                  # freeze/unfreeze/check
    txid = Column(String(128), nullable=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
