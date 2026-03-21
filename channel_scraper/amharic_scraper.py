# channel_scraper/amharic_scraper.py
"""
Scraper for Amharic Christian book channels.
Parses captions to extract author and category using common Amharic patterns.
Run locally: python channel_scraper/amharic_scraper.py
"""
import sys
import os
import time
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
from telethon.errors import FloodWaitError
from dotenv import load_dotenv
from database.db import insert_book, book_exists
from database.models import create_tables, migrate_add_language_column

# -------------------------------
# 🔹 Load Environment Variables
# -------------------------------
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHAT_ID = int(os.getenv("ARCHIVE_CHAT_ID"))

# -------------------------------
# 🔹 Amharic Channels to Scrape
# -------------------------------
AMHARIC_CHANNELS = [
    "@amharicspritualbooks",
    # Add more Amharic channels here as needed
]

# Allowed document types
ALLOWED_MIME_TYPES = [
    "application/pdf",
    "application/epub+zip",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/x-mobipocket-ebook",
]

# -------------------------------
# 🔹 Initialize
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
create_tables()
migrate_add_language_column()
client = TelegramClient('scraper_session', API_ID, API_HASH)

# Delay between forwards to avoid flood bans
FORWARD_DELAY = 2  # seconds


# -------------------------------
# 🔹 Caption-Based Detection
# -------------------------------
def extract_file_name(document):
    """Extract filename from document attributes."""
    for attr in document.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            return attr.file_name
    return "Unknown_File"


def extract_author_from_caption(caption):
    """
    Try to extract author from Amharic caption patterns like:
    - 👤ጸሐፊ፦ ዶ/ር መለሰ ወጉ
    """
    if not caption:
        return "Unknown"

    patterns = [
        r'(?:👤|✍️|✍)?\s*(?:ደራሲ|ጸሐፊ|ፀሐፊ|Author|author|By|by).{0,5}?(?:፦|:-|:|：|-|–|—)\s*([^\n]+)',
        r'✍️\s*([^\n]+)',
        r'✍\s*([^\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            author = match.group(1).strip()
            # Clean up trailing emojis or markers
            author = re.sub(r'[📚📖📔🔥✨💡⭐️🙏👤📥]+$', '', author).strip()
            if author:
                return author

    return "Unknown"


def extract_title_from_caption(caption, file_name):
    """
    Try to extract title from Amharic caption patterns like:
    - 📔ርዕስ:-ካርቦን-ኮፒ ክርስትና
    """
    if not caption:
        return clean_filename(file_name)

    patterns = [
        r'(?:📔|📚)?\s*(?:መጽሐፍ\s*(?:ስም)?|ርዕስ|Title|title).{0,5}?(?:፦|:-|:|：|-|–|—)\s*([^\n]+)',
        r'📚\s*([^\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, caption, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            title = re.sub(r'[📚📖📔🔥✨💡⭐️🙏👤📥]+$', '', title).strip()
            if title:
                return title

    return clean_filename(file_name)


def clean_filename(name):
    """Remove file extension and clean up the filename for use as title."""
    name = os.path.splitext(name)[0]
    name = name.replace('_', ' ').replace('-', ' ')
    return name.strip()


def detect_amharic_category(text):
    """
    Detect category from caption/filename using Amharic and English keywords.
    """
    if not text:
        return "Other"

    text_lower = text.lower()

    category_rules = {
        # Extended Amharic keywords
        "መጽሐፍ ቅዱስ": "መጽሐፍ ቅዱስ ጥናት",     # Bible Study
        "ጸሎት": "ጸሎት",                      # Prayer
        "ስብከት": "ስብከት",                    # Sermons
        "ነገረ መለኮት": "ነገረ መለኮት",           # Theology
        "ሥነ-መለኮት": "ነገረ መለኮት",          
        "ታሪክ": "የቤተክርስቲያን ታሪክ",          # Church History
        "ወንጌል": "ወንጌል",                    # Gospel
        "እምነት": "እምነት",                    # Faith
        "ጥምቀት": "ጥምቀት",                   # Baptism
        "ትምህርት": "ትምህርት",                 # Teaching/Doctrine
        "መዝሙር": "መዝሙር",                   # Hymns/Psalms
        "ክርስቲያናዊ": "ክርስቲያናዊ ሕይወት",      # Christian Living
        "ጋብቻ": "ጋብቻ እና ቤተሰብ",            # Marriage & Family
        "ቤተሰብ": "ጋብቻ እና ቤተሰብ",           
        "ውግያ": "መንፈሳዊ ውግያ",              # Spiritual Warfare
        "ጭንቀት": "የአእምሮ ጤና እና መጽናናት", # Mental Health/Comfort
        "ስሕተት": "የስህተት ትምህርት መከላከያ",  # Apologetics/Cults
        "መከላከያ": "የስህተት ትምህርት መከላከያ",
        
        # English keywords (some channels mix languages)
        "bible": "መጽሐፍ ቅዱስ ጥናት",
        "prayer": "ጸሎት",
        "sermon": "ስብከት",
        "theology": "ነገረ መለኮት",
        "devotional": "መንፈሳዊ ንባብ",
        "commentary": "ትርጓሜ",
        "history": "የቤተክርስቲያን ታሪክ",
    }

    for keyword, category in category_rules.items():
        if keyword in text or keyword in text_lower:
            return category

    return "Other"


# -------------------------------
# 🔹 Main Scraping Logic
# -------------------------------
def scrape_amharic_channel(channel_username, limit=1000):
    """Scrape a single Amharic channel."""
    print(f"\n📡 Scraping Amharic channel: {channel_username}")
    forwarded_count = 0
    skipped_count = 0

    for message in client.iter_messages(channel_username, limit=limit):
        if not (message.media and isinstance(message.media, MessageMediaDocument)):
            continue

        mime_type = message.media.document.mime_type
        if mime_type not in ALLOWED_MIME_TYPES:
            continue

        file_name = extract_file_name(message.media.document)
        caption = message.message or ""

        # Check if already exists
        if book_exists(file_name):
            print(f"⏩ Skipping existing: {file_name}")
            skipped_count += 1
            continue

        # Extract metadata from caption
        author = extract_author_from_caption(caption)
        title = extract_title_from_caption(caption, file_name)
        category = detect_amharic_category(f"{file_name} {caption}")
        date = message.date

        # Forward to archive channel
        try:
            forwarded = client.forward_messages(
                ARCHIVE_CHAT_ID,
                message.id,
                from_peer=channel_username
            )
        except FloodWaitError as e:
            print(f"⏳ Flood wait: sleeping for {e.seconds} seconds...")
            time.sleep(e.seconds)
            forwarded = client.forward_messages(
                ARCHIVE_CHAT_ID,
                message.id,
                from_peer=channel_username
            )

        # Get message_id from forwarded message
        message_id = None
        if forwarded:
            if isinstance(forwarded, list):
                message_id = forwarded[0].id
            else:
                message_id = forwarded.id

        if not message_id:
            print(f"❌ Failed to forward: {file_name}")
            continue

        # Insert into DB with language='Amharic'
        insert_book(
            title=title,
            caption=caption,
            author=author,
            category=category,
            mime_type=mime_type,
            file_id=str(message_id),
            date=str(date),
            language='Amharic'
        )

        forwarded_count += 1
        print(f"✅ [{forwarded_count}] {title} (by {author}) [{category}]")

        # Delay to avoid flood ban
        time.sleep(FORWARD_DELAY)

    print(f"\n🎯 Finished: {forwarded_count} Amharic books forwarded!")
    print(f"⏩ Skipped {skipped_count} existing books.")


def scrape_all_amharic_channels(limit=1000):
    """Scrape all configured Amharic channels."""
    with client:
        for channel in AMHARIC_CHANNELS:
            scrape_amharic_channel(channel, limit=limit)


# -------------------------------
# 🔹 Run Script
# -------------------------------
if __name__ == "__main__":
    print("📖 Amharic Christian Books Scraper")
    print("=" * 40)
    scrape_all_amharic_channels(limit=5000)
