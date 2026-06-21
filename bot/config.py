"""
Bot 配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
ENERGY_PRICE_PER_DAY = float(os.getenv("ENERGY_PRICE_PER_DAY", "0.5"))  # TRX per 1000 energy per day
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@your_support")
