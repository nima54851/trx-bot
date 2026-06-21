"""
数据库连接 — 使用 SQLite（Railway免配置）
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Railway提供$DATABASE_URL，本地开发用SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./trxbot.db"   # 本地开发：当前目录下的 trxbot.db
)

# SQLite不支持pool_pre_ping
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    from config import settings
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
