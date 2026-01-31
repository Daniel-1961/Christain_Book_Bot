from flask import Flask, request
from telegram import Update
import asyncio
import threading

from bot.bot_app import create_application


app = Flask(__name__)

application = None

def get_application():
    """Return the telegram Application, creating it on first use."""
    global application
    if application is None:
        application = create_application()
    return application

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
    app_obj = get_application()
    update = Update.de_json(
        request.get_json(force=True),
        app_obj.bot
    )

    # Schedule async processing safely
    asyncio.run_coroutine_threadsafe(
        app_obj.process_update(update),
        loop
    )

    return "OK", 200
