"""
FastAPI 后端入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from api import orders, energy, admin
from database import engine, Base

app = FastAPI(
    title="TRX Energy Bot API",
    description="TRX能量租赁系统后端API",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库初始化
Base.metadata.create_all(bind=engine)

# 挂载静态文件（前端）
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(os.path.dirname(BASE_DIR), "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# 注册路由
app.include_router(orders.router, prefix="/api/orders", tags=["订单"])
app.include_router(energy.router, prefix="/api/energy", tags=["能量"])
app.include_router(admin.router, prefix="/api/admin", tags=["管理"])


@app.get("/")
async def root():
    return {"message": "TRX Energy Bot API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
