from flask import Flask, request
from telegram import Update
import asyncio

from bot.bot_app import create_application

app = Flask(__name__)
application = create_application()

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(
        request.get_json(force=True),
        application.bot
    )
    asyncio.run(application.process_update(update))
    return "OK", 200

if __name__ == "__main__":
    app.run(port=8000)
