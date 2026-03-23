# bot/main.py
"""
Local development entry point — runs the bot in POLLING mode.
For production (PythonAnywhere), use the Flask webhook via webhook_app.py.
"""
import sys
import os

# Ensure the project root is on sys.path so 'bot' package resolves
# when running this file directly (e.g. python bot/main.py)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
)
from dotenv import load_dotenv

# Import all handlers from the shared handlers module
from bot.handlers import start, about, search_command, callback_handler

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


from bot.bot_app import create_application

def main():
    """Run the bot in polling mode (for local development only)."""
    app = create_application()
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    print("🚀 Bot started in POLLING mode (local development)...")
    main()
