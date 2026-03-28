#  Christian Book Bot
A **Telegram bot** that helps Christians easily **discover, browse, and access Christian books** from public Telegram channels — including writings from the **early church fathers**, **medieval theologians**, and **modern evangelical authors**.  

The goal is to build a **free, accessible digital library** where users can search books by *author*, *category*, or *keyword*, and download them directly in Telegram.

---
## Features

- 📚 **Browse by author, category, or keyword**
- 🔍 **Search** books quickly
- 💾 **Download** books directly from Telegram
- 🗂️ Uses a **database** for fast, organized retrieval
- 🕊️ Supports **English** and **Amharic** collections
- ⚙️ Built with **Python** and **python-telegram-bot**

---
## Tech Stack

| Component | Technology |
|------------|-------------|
| **Language** | Python 3 |
| **Framework** | python-telegram-bot |
| **Database** | SQLite |
| **Deployment** | PythonAnywhere / Render / Railway |
| **Scraper** | Custom Telegram scraper for collecting book data |

---
## Getting Started

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Daniel-1961/Christain_Book_Bot.git
cd Christain_Book_Bot
```
### 1️⃣ Create Enviroment variable
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
### Install dependacies
```bash

pip install -r requirements.txt
```

### 4️⃣ Add environment variables
```bash

BOT_TOKEN=your_telegram_bot_token
ARCHIVE_CHAT_ID=your_private_channel_id
DB_PATH=data/books.db
```
### 5️⃣ Run the bot
 ```bash
 python bot/main.py
```
## Project Structure
```markdown
Christain_Book_Bot/
│
├── bot/
│   ├── main.py              # Main bot script
│   ├── utils.py             # Helper functions
│   ├── db.py                # Database interactions
│
├── data/
│   └── books.db             # SQLite database (not included in repo)
│
├── requirements.txt         # Dependencies
├── .env.example             # Example environment variables
└── README.md
```
##  Future Improvements

🌍 Add more languages (Amharic and English expansion)

🧠 Implement semantic search for better keyword matching

🪶 Improve UI and user experience

☁️ Move to a 24/7 cloud deployment (Render / Railway)

🧾 Add admin dashboard for managing books
