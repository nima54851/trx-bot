"""
Bot 状态常量
"""
from enum import Enum

class BotState(Enum):
    WAITING_ADDRESS = 1       # 等待用户输入TRX地址
    WAITING_ENERGY = 2        # 等待用户输入能量数量
    WAITING_DAYS = 3          # 等待用户输入天数
    CONFIRM_ORDER = 4         # 确认订单

STATES = BotState

# 能量档位选项
ENERGY_OPTIONS = [
    ("5,000 能量 (基础)", 5000),
    ("10,000 能量 (标准)", 10000),
    ("50,000 能量 (高级)", 50000),
    ("100,000 能量 (专业)", 100000),
    ("200,000 能量 (企业)", 200000),
    ("500,000 能量 (旗舰)", 500000),
]

# 天数选项
DAY_OPTIONS = [
    ("1天", 1),
    ("3天", 3),
    ("7天", 7),
    ("15天", 15),
    ("30天", 30),
]
