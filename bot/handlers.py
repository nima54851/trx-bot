"""
Telegram Bot 命令处理器
"""
import os
import sys
import httpx
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from keyboards import (
    energy_keyboard, days_keyboard, confirm_order_keyboard,
    main_menu_keyboard, admin_keyboard
)
from config import BACKEND_URL, ENERGY_PRICE_PER_DAY, SUPPORT_USERNAME

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 全局菜单
# ─────────────────────────────────────────────

async def start_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"👋 欢迎，{user.first_name}！\n\n"
        f"⚡ *TRX 能量租赁机器人*\n\n"
        f"在这里你可以租用 TRON 链能量，无需抵押冻结你的 TRX，"
        f"立即使用，费用低至 *{ENERGY_PRICE_PER_DAY} TRX/天/1000能量*\n\n"
        f"选择下方功能开始："
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


async def help_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ *使用帮助*\n\n"
        "⚡ **能量是什么？**\n"
        "TRON链上每笔交易消耗能量，租用能量可以省去自己抵押冻结TRX的麻烦。\n\n"
        "💰 **费用怎么算？**\n"
        "费用 = 能量数 × 天数 × 单价\n"
        f"单价：{ENERGY_PRICE_PER_DAY} TRX / 1000能量 / 天\n\n"
        "📋 **使用流程**\n"
        "1. 点击「购买能量」\n"
        "2. 选择能量数量和天数\n"
        "3. 向指定地址转入TRX\n"
        "4. 等待确认，能量立即到账\n\n"
        "⚠️ 注意：最小租用5,000能量，最多500,000能量\n\n"
        f"📞 问题联系：{SUPPORT_USERNAME}"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


# ─────────────────────────────────────────────
# 购买能量
# ─────────────────────────────────────────────

async def buy_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        "⚡ *选择能量数量*\n\n"
        "请从下方选择你需要的能量数量：\n"
        "（租用天数在下一步选择）"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=energy_keyboard())


async def wallet_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"💰 *我的钱包*\n\n"
        f"Telegram ID：`{user.id}`\n\n"
        f"📌 购买能量时，需要提供你的 *TRX 接收地址*（你自己的波场钱包地址）\n\n"
        "💡 提示：\n"
        "• 租用能量不会改变你的地址余额\n"
        "• 能量直接充入你指定的合约地址\n"
        "• 租用完成后TRX原路返回"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def orders_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BACKEND_URL}/api/orders/user/{user.id}", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            orders = data.get("orders", [])
            if not orders:
                text = "📋 你还没有任何订单"
            else:
                lines = ["📋 *我的订单*\n"]
                for o in orders[:5]:
                    status_emoji = {"pending": "⏳", "paid": "✅", "rented": "⚡", "expired": "⏰", "cancelled": "❌"}.get(o.get("status", ""), "❓")
                    lines.append(
                        f"{status_emoji} #{o.get('order_id', '')[:12]}...\n"
                        f"  ⚡{o.get('energy_amount', 0)}能量 / {o.get('rent_days', 0)}天\n"
                        f"  💰 {o.get('trx_amount', 0)} TRX\n"
                    )
                text = "\n".join(lines)
        else:
            text = "⚠️ 暂时无法获取订单，请稍后再试"
    except Exception as e:
        logger.error(f"获取订单失败: {e}")
        text = "⚠️ 服务暂不可用，请稍后再试"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


async def query_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """查询订单：/query <订单号>"""
    parts = update.message.text.split()
    if len(parts) < 2:
        await update.message.reply_text("用法：/query <订单号>\n示例：/query LE123456ABC")
        return

    order_id = parts[1]
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BACKEND_URL}/api/orders/{order_id}", timeout=10)
        if resp.status_code == 200:
            o = resp.json()
            status_emoji = {"pending": "⏳", "paid": "✅", "rented": "⚡", "expired": "⏰"}.get(o.get("status", ""), "❓")
            text = (
                f"🔍 *订单查询结果*\n\n"
                f"订单号：`{o.get('order_id', '')}`\n"
                f"状态：{status_emoji} {o.get('status', '')}\n"
                f"能量：⚡ {o.get('energy_amount', 0)}\n"
                f"天数：📅 {o.get('rent_days', 0)} 天\n"
                f"金额：💰 {o.get('trx_amount', 0)} TRX\n"
                f"支付地址：`{o.get('deposit_address', '')}`"
            )
        else:
            text = "❌ 订单不存在"
    except Exception:
        text = "⚠️ 查询失败，请稍后再试"

    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())


# ─────────────────────────────────────────────
# Callback Query 处理器（主入口）
# ─────────────────────────────────────────────

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """统一处理所有按钮回调"""
    query = update.callback_query
    await query.answer()
    data = query.data

    user = query.from_user

    # 主菜单按钮
    if data == "back_main" or data.startswith("menu_"):
        text = (
            f"👋 欢迎，{user.first_name}！\n\n"
            f"⚡ *TRX 能量租赁机器人*\n\n"
            f"选择功能："
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        return

    if data == "menu_buy":
        text = "⚡ *选择能量数量*\n\n请选择你需要的能量："
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=energy_keyboard())
        return

    if data == "menu_wallet":
        text = (
            f"💰 *我的钱包*\n\n"
            f"Telegram ID：`{user.id}`\n\n"
            f"购买时需提供你的 TRX 接收地址。"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        return

    if data == "menu_orders":
        await query.edit_message_text("📋 正在加载订单...")
        ctx.args = []
        await orders_handler(update, ctx)
        return

    if data == "menu_pricing":
        text = (
            "📊 *能量定价表*\n\n"
            "| 能量 | 1天 | 3天 | 7天 | 15天 | 30天 |\n"
            "|---|---|---|---|---|---|\n"
            "| 5,000 | 2.5 | 7.5 | 17.5 | 37.5 | 75 |\n"
            "| 10,000 | 5 | 15 | 35 | 75 | 150 |\n"
            "| 50,000 | 25 | 75 | 175 | 375 | 750 |\n"
            "| 100,000 | 50 | 150 | 350 | 750 | 1500 |\n"
            "\n*单位：TRX*"
        )
        await query.edit_message_text(text, parse_mode="MarkdownV2", reply_markup=main_menu_keyboard())
        return

    if data == "menu_help":
        text = (
            "❓ *使用帮助*\n\n"
            "1️⃣ 点击「购买能量」\n"
            "2️⃣ 选择能量数量和天数\n"
            "3️⃣ 向指定地址转入TRX\n"
            "4️⃣ 等待确认，能量立即到账\n\n"
            f"📞 {SUPPORT_USERNAME}"
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
        return

    # 能量选择
    if data.startswith("energy_"):
        energy = int(data.split("_")[1])
        ctx.user_data["selected_energy"] = energy
        text = (
            f"⚡ 你选择了 *{energy:,} 能量*\n\n"
            f"现在选择租用天数："
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=days_keyboard(energy))
        return

    # 天数选择 → 创建订单
    if data.startswith("days_"):
        parts = data.split("_")
        energy = int(parts[1])
        days = int(parts[2])
        ctx.user_data["selected_energy"] = energy
        ctx.user_data["selected_days"] = days

        price = energy * days * ENERGY_PRICE_PER_DAY / 1000
        text = (
            f"📋 *订单确认*\n\n"
            f"⚡ 能量：{energy:,}\n"
            f"📅 天数：{days} 天\n"
            f"💰 总价：*{price:.4f} TRX*\n\n"
            f"请向以下地址转入 *{price:.4f} TRX*：\n"
            f"`正在生成支付地址...`\n\n"
            f"⏳ 等待支付..."
        )
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=confirm_order_keyboard("pending"))

        # 调用后端创建订单
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{BACKEND_URL}/api/orders/create",
                    json={
                        "user_id": user.id,
                        "trx_address": "TX...",  # TODO: 用户输入
                        "energy_amount": energy,
                        "rent_days": days,
                        "username": user.username,
                    },
                    timeout=15,
                )
                if resp.status_code == 200:
                    order_data = resp.json()
                    new_text = (
                        f"📋 *订单已创建*\n\n"
                        f"订单号：`{order_data['order_id']}`\n"
                        f"⚡ 能量：{energy:,}\n"
                        f"📅 天数：{days} 天\n"
                        f"💰 总价：*{price:.4f} TRX*\n\n"
                        f"请向上述地址转入 *{price:.4f} TRX*，\n"
                        f"支付完成后点击「已支付」。"
                    )
                    await query.edit_message_text(
                        new_text,
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("✅ 已支付", callback_data=f"paid_{order_data['order_id']}")],
                            [InlineKeyboardButton("❌ 取消", callback_data="back_main")],
                        ])
                    )
                else:
                    await query.edit_message_text(f"❌ 创建订单失败：{resp.text}")
        except Exception as e:
            logger.error(f"创建订单失败: {e}")
            await query.edit_message_text(f"❌ 服务暂不可用：{str(e)[:100]}")
        return

    # 支付确认
    if data.startswith("paid_"):
        order_id = data.replace("paid_", "")
        await query.edit_message_text(f"⏳ 正在确认支付 `{order_id}`...", parse_mode="Markdown")
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(f"{BACKEND_URL}/api/orders/{order_id}", timeout=10)
                if resp.status_code == 200:
                    o = resp.json()
                    status = o.get("status", "")
                    if status == "pending":
                        await query.edit_message_text(
                            "⏳ 订单仍在pending状态，请确认已转账后重试",
                            parse_mode="Markdown",
                            reply_markup=InlineKeyboardMarkup([
                                [InlineKeyboardButton("🔄 重新查询", callback_data=f"paid_{order_id}")],
                                [InlineKeyboardButton("🏠 返回主页", callback_data="back_main")],
                            ])
                        )
                    else:
                        status_emoji = {"paid": "✅", "rented": "⚡"}.get(status, "❓")
                        await query.edit_message_text(
                            f"{status_emoji} *订单已确认！*\n\n订单 {order_id} 状态：{status}",
                            parse_mode="Markdown",
                            reply_markup=main_menu_keyboard()
                        )
        except Exception as e:
            await query.edit_message_text(f"⚠️ 查询失败：{str(e)[:100]}")
        return

    if data.startswith("cancel_"):
        await query.edit_message_text("❌ 订单已取消", reply_markup=main_menu_keyboard())
        return
