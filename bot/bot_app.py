# bot/bot_app.py
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler
)
from dotenv import load_dotenv

# import your existing handlers
from bot.main import start, about, callback_handler

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

def create_application():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # register handlers (same as before)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CallbackQueryHandler(callback_handler))

    return application
