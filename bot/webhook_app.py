# bot/webhook_app.py
import logging
import asyncio

from flask import Flask, request
from telegram import Update

from bot.bot_app import create_application

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ----------------------------
# Create Flask app
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Telegram Application (created lazily, initialized once)
# ----------------------------
_telegram_app = None
_initialized = False

# Single persistent event loop (no threads needed)
_loop = asyncio.new_event_loop()


def get_application():
    """Return the Telegram Application, creating and initializing it on first use."""
    global _telegram_app, _initialized
    if _telegram_app is None:
        _telegram_app = create_application()

    if not _initialized:
        _loop.run_until_complete(_telegram_app.initialize())
        _initialized = True
        logger.info("Telegram Application initialized successfully")

    return _telegram_app


# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def health():
    """Health check endpoint."""
    return "Christian Books Bot is running! 📚", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive Telegram updates via webhook."""
    try:
        telegram_app = get_application()
        update = Update.de_json(
            request.get_json(force=True),
            telegram_app.bot,
        )

        # Process update synchronously on our persistent event loop
        _loop.run_until_complete(telegram_app.process_update(update))

        return "OK", 200
    except Exception:
        logger.exception("Error processing webhook update")
        return "Internal Server Error", 500
