"""
Telegram Bot 入口
"""
import os
import sys
import logging
from dotenv import load_dotenv

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_dotenv()

import asyncio
from telegram import Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters, ContextTypes,
    ConversationHandler
)
from handlers import (
    start_handler, help_handler, buy_handler,
    wallet_handler, orders_handler, admin_handler,
    query_handler
)
from states import STATES

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Bot启动后设置命令菜单"""
    commands = [
        BotCommand("start", "🚗 启动机器人"),
        BotCommand("buy", "⚡ 购买能量"),
        BotCommand("wallet", "💰 我的钱包"),
        BotCommand("orders", "📋 我的订单"),
        BotCommand("help", "❓ 使用帮助"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN 未设置！")
        sys.exit(1)

    app = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    # 命令处理器
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("buy", buy_handler))
    app.add_handler(CommandHandler("wallet", wallet_handler))
    app.add_handler(CommandHandler("orders", orders_handler))
    app.add_handler(CommandHandler("query", query_handler))

    logger.info("🤖 TRX Energy Bot 启动中...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
