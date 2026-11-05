# bot/bot_app.py
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters
)
from dotenv import load_dotenv

from bot.handlers import (
    start, about, search_command, help_command, language_command, donate_command,
    stats_command, callback_handler, precheckout_callback, successful_payment_callback
)
from bot.admin import admin_stats, broadcast_command, add_book_conv_handler, export_users_command, pending_books_command

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


def create_application():
    """Build and configure the Telegram Application with all handlers."""
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # User commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("about", about))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("donate", donate_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Admin commands
    application.add_handler(CommandHandler("adminstats", admin_stats))
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("export", export_users_command))
    application.add_handler(CommandHandler("pending", pending_books_command))
    
    # Book upload conversation handler (admin only)
    application.add_handler(add_book_conv_handler)
    
    # Callback handlers
    application.add_handler(CallbackQueryHandler(callback_handler))

    # Payment Handlers
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback))

    return application
