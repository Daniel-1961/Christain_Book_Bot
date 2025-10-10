# channel_scraper/scraper.py

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
import requests
import os
from dotenv import load_dotenv
from database.db import insert_book
from database.models import create_tables

# -------------------------------
# 🔹 Load Environment Variables
# -------------------------------
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHAT_ID= os.getenv("ARCHIVE_CHAT_ID")

# -------------------------------
# 🔹 Initialize Directories and DB
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'data', 'files')
os.makedirs(FILES_DIR, exist_ok=True)

create_tables()
client = TelegramClient('scraper_session', API_ID, API_HASH)

# -------------------------------
# 🔹 Category and Author Rules
# -------------------------------
CATEGORY_RULES = {
    "systematic": "Systematic Theology",
    "theology": "Systematic Theology",
    "commentary": "Commentary",
    "confession": "Confession",
    "creed": "Creeds",
    "devotional": "Devotional",
    "catechism": "Catechism",
    "sermon": "Sermons",
    "church": "Church History",
    "covenant": "Covenant Theology",
    "eschatology": "Eschatology",
    "christ": "Christology",
    "salvation": "Soteriology",
    "ethics": "Christian Ethics",
    "prayer": "Prayer & Spiritual Growth",
    "apologetic": "Apologetics",
    "doctrine": "Doctrinal Studies",
    "grace": "Grace & Salvation",
    "faith": "Faith & Justification",
    "worship": "Worship & Liturgy",
    "reformation": "Reformation History",
    "spiritual": "Spiritual Growth",
    "gospel": "Gospel Studies",
    "discipleship": "Discipleship",
}

AUTHOR_RULES = {
    "calvin": "John Calvin",
    "luther": "Martin Luther",
    "spurgeon": "Charles Spurgeon",
    "packer": "J.I. Packer",
    "sproul": "R.C. Sproul",
    "pink": "A.W. Pink",
    "berkhof": "Louis Berkhof",
    "bavinck": "Herman Bavinck",
    "kuper": "Abraham Kuyper",
    "owen": "John Owen",
    "watson": "Thomas Watson",
    "bunyan": "John Bunyan",
    "ferguson": "Sinclair Ferguson",
    "macarthur": "John MacArthur",
    "lloyd": "Martyn Lloyd-Jones",
    "piper": "John Piper",
    "ryle": "J.C. Ryle",
    "stott": "John Stott",
    "carson": "D.A. Carson",
    "edwards": "Jonathan Edwards",
    "warfield": "B.B. Warfield",
    "hodge": "Charles Hodge",
    "turretin": "Francis Turretin",
    "beza": "Theodore Beza",
    "murray": "John Murray",
    "vos": "Geerhardus Vos",
    "ridderbos": "Herman Ridderbos",
    "boston": "Thomas Boston",
    "perkins": "William Perkins",
    "goodwin": "Thomas Goodwin",
    "sibbes": "Richard Sibbes",
    "brakel": "Wilhelmus à Brakel",
    "gill": "John Gill",
}

# -------------------------------
# 🔹 Helper Functions
# -------------------------------
def extract_file_name(document):
    for attr in document.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            return attr.file_name
    return "Unknown_File"

def detect_category(text):
    text = text.lower()
    for keyword, category in CATEGORY_RULES.items():
        if keyword in text:
            return category
    return "Other"

def detect_author(text):
    text = text.lower()
    for keyword, author in AUTHOR_RULES.items():
        if keyword in text:
            return author
    return "Unknown"

# -------------------------------
# 🔹 Upload Function (Synchronous)
# -------------------------------
def upload_to_telegram(local_path, file_name, author, category):
    """Uploads a document to Telegram using the Bot API (synchronously)."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(local_path, "rb") as file_data:
        response = requests.post(
            url,
            data={
                "chat_id":ARCHIVE_CHAT_ID,
                "caption": f"{file_name}\nAuthor: {author}\nCategory: {category}"
            },
            files={"document": file_data}
        )
    if response.status_code == 200:
        result = response.json().get("result", {})
        if "document" in result:
            return result["document"]["file_id"]
    else:
        print(f"⚠️ Upload failed ({response.status_code}): {response.text}")
    return None

# -------------------------------
# 🔹 Main Scraping Logic
# -------------------------------
def scrape_channel(limit=1000):
    allowed_mime_types = [
        "application/pdf",
        "application/epub+zip",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/x-mobipocket-ebook",
       # "application/zip",
       # "application/x-rar-compressed",
    ]

    with client:
        print("📡 Scraping Telegram channel for Reformed books...")
        scraped_count = 0

        for message in client.iter_messages(CHANNEL_USERNAME, limit=limit):
            if not (message.media and isinstance(message.media, MessageMediaDocument)):
                continue

            mime_type = message.media.document.mime_type
            if mime_type not in allowed_mime_types:
                continue

            file_name = extract_file_name(message.media.document)
            caption = message.message or ""
            category = detect_category(f"{file_name} {caption}")
            author = detect_author(f"{file_name} {caption}")
            date = message.date

            local_path = os.path.join(FILES_DIR, file_name)
            if not os.path.exists(local_path):
                print(f"⬇️ Downloading: {file_name}")
                client.download_media(message, file=local_path)

            file_id = upload_to_telegram(local_path, file_name, author, category)
            if not file_id:
                print(f"❌ Failed to upload {file_name}")
                continue

            # Store in DB
            insert_book(
                title=file_name,
                caption=caption,
                author=author,
                category=category,
                mime_type=mime_type,
                file_id=file_id,
                date=str(date)
            )

            scraped_count += 1
            print(f"✅ Uploaded {file_name} ({scraped_count})")

            # Optional: remove local file
            try:
                os.remove(local_path)
            except Exception:
                pass

        print(f"\n🎯 Finished scraping and uploading {scraped_count} books!")

# -------------------------------
# 🔹 Run Script
# -------------------------------
if __name__ == "__main__":
    scrape_channel(limit=5000)
