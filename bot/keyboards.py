"""
Inline 键盘按钮定义
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def energy_keyboard():
    """能量选择键盘"""
    from states import ENERGY_OPTIONS
    keyboard = []
    for label, value in ENERGY_OPTIONS:
        keyboard.append([InlineKeyboardButton(label, callback_data=f"energy_{value}")])
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def days_keyboard(selected_energy: int):
    """天数选择键盘"""
    from states import DAY_OPTIONS
    keyboard = []
    for label, value in DAY_OPTIONS:
        keyboard.append([InlineKeyboardButton(label, callback_data=f"days_{selected_energy}_{value}")])
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="back_main")])
    return InlineKeyboardMarkup(keyboard)


def confirm_order_keyboard(order_id: str):
    """订单确认键盘"""
    keyboard = [
        [
            InlineKeyboardButton("✅ 已支付", callback_data=f"paid_{order_id}"),
            InlineKeyboardButton("❌ 取消", callback_data=f"cancel_{order_id}"),
        ],
        [InlineKeyboardButton("🔙 返回主页", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard():
    """主菜单"""
    keyboard = [
        [InlineKeyboardButton("⚡ 购买能量", callback_data="menu_buy")],
        [InlineKeyboardButton("💰 我的钱包", callback_data="menu_wallet")],
        [InlineKeyboardButton("📋 我的订单", callback_data="menu_orders")],
        [InlineKeyboardButton("📊 价格表", callback_data="menu_pricing")],
        [InlineKeyboardButton("❓ 帮助", callback_data="menu_help")],
    ]
    return InlineKeyboardMarkup(keyboard)


def admin_keyboard():
    """管理员键盘"""
    keyboard = [
        [InlineKeyboardButton("📊 今日统计", callback_data="admin_stats")],
        [InlineKeyboardButton("📋 全部订单", callback_data="admin_orders")],
        [InlineKeyboardButton("💰 收入报表", callback_data="admin_revenue")],
        [InlineKeyboardButton("🔙 返回", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
