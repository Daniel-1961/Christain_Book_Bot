from flask import Flask, request
from telegram import Update
import asyncio
import threading

from bot.bot_app import create_application

# ----------------------------
# Create Flask app
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Create Telegram application
# ----------------------------
application = create_application()

# ----------------------------
# Create ONE event loop (important!)
# ----------------------------
loop = asyncio.new_event_loop()

def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

# ----------------------------
# Webhook endpoint
# ----------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        application.bot
    )

    # Schedule async processing safely
    asyncio.run_coroutine_threadsafe(
        application.process_update(update),
        loop
    )

    return "OK", 200
