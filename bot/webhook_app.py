# bot/webhook_app.py
import logging
import asyncio
import threading

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
# (WSGI servers like PythonAnywhere expect a callable named `app` or `application`)
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Telegram Application (created lazily, initialized once)
# ----------------------------
_telegram_app = None
_initialized = False


def get_application():
    """Return the Telegram Application, creating and initializing it on first use."""
    global _telegram_app, _initialized
    if _telegram_app is None:
        _telegram_app = create_application()

    if not _initialized:
        # Initialize the application so the bot object is fully ready
        future = asyncio.run_coroutine_threadsafe(
            _telegram_app.initialize(), loop
        )
        future.result(timeout=30)  # Wait up to 30s for init
        _initialized = True
        logger.info("Telegram Application initialized successfully")

    return _telegram_app


# ----------------------------
# Create ONE persistent event loop in a background thread
# ----------------------------
loop = asyncio.new_event_loop()


def _start_loop(event_loop):
    asyncio.set_event_loop(event_loop)
    event_loop.run_forever()


threading.Thread(target=_start_loop, args=(loop,), daemon=True).start()



# ----------------------------
# Routes
# ----------------------------
@app.route("/")
def health():
    """Health check endpoint — useful for uptime monitoring."""
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

        # Schedule async processing on the background event loop
        asyncio.run_coroutine_threadsafe(
            telegram_app.process_update(update),
            loop,
        )

        return "OK", 200
    except Exception:
        logger.exception("Error processing webhook update")
        return "Internal Server Error", 500
