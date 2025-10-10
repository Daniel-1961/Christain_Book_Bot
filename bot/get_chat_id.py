from telegram import Bot
import os
from dotenv import load_dotenv

# -------------------------------
# 🔹 Load environment variables
# -------------------------------
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

print("Send any message in your private channel first...")
updates = bot.get_updates()
for u in updates:
    if u.channel_post:
        print("Your channel ID is:", u.channel_post.chat.id)
