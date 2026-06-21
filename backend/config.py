"""
后端配置文件
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Telegram
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # TRON
    TRON_API_KEY: str = os.getenv("TRON_API_KEY", "")
    TRON_NETWORK: str = os.getenv("TRON_NETWORK", "mainnet")  # mainnet / nile / shasta
    TRON_WALLET_PRIVATE_KEY: str = os.getenv("TRON_WALLET_PRIVATE_KEY", "")
    TRON_WALLET_ADDRESS: str = os.getenv("TRON_WALLET_ADDRESS", "")

    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://trxbot:trxbotpass@localhost:5432/trxbot"
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # 能量配置
    ENERGY_PRICE_PER_DAY: float = float(os.getenv("ENERGY_PRICE_PER_DAY", "0.5"))  # TRX/天/1000能量
    MIN_ENERGY: int = int(os.getenv("MIN_ENERGY", "5000"))
    MAX_ENERGY: int = int(os.getenv("MAX_ENERGY", "500000"))
    MIN_RENT_DAYS: int = 1
    MAX_RENT_DAYS: int = 30

    # 管理员
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # 安全
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")


settings = Settings()
