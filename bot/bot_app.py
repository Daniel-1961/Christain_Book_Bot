# bot/bot_app.py
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)
from dotenv import load_dotenv

from bot.handlers import start, about, search_command, callback_handler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


def create_application():
    """Build and configure the Telegram Application with all handlers."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CallbackQueryHandler(callback_handler))

    return application
