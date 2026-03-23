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


def is_english_book(caption):
    """
    Detect if a caption describes an English-language book.
    We skip these in the Amharic scraper so only Amharic books are collected.
    English books are handled by the separate English scraper.
    """
    if not caption:
        return False

    # If the caption has English keywords like "Book", "Author", "Page", "Size"
    english_markers = [
        r'(?:^|\n)\s*Book\s*[:：፦\-–—]',
        r'(?:^|\n)\s*👤\s*Author\s*[:：፦\-–—]',
        r'(?:^|\n)\s*📑\s*Page\s*[:：፦\-–—]',
        r'(?:^|\n)\s*💾\s*Size\s*[:：፦\-–—]',
    ]
    english_count = sum(1 for p in english_markers if re.search(p, caption, re.IGNORECASE))
    if english_count >= 2:
        return True

    return False


def extract_author_from_caption(caption):
    """
    Extract author from Amharic caption patterns.
    Handles separators: ፦  :-  :  -  –  —
    Handles emoji prefixes: 👤
    
    Examples:
        👤ደራሲ፦ቻርለስ ዳየር(ዶ/ር)
        👤ጸሐፊ:-ጳውሎስ ፈቃዱ
        👤ጸሐፊ፦ንጉሴ ቡልቻ(ጋሽ)
    """
    if not caption:
        return "Unknown"

    # Unified separator group that covers all observed formats
    sep = r'[:：፦]\s*|\s*:-\s*|\s*[–—]\s*'

    patterns = [
        # 👤ደራሲ፦... or 👤ጸሐፊ:-... (emoji glued to keyword)
        rf'👤\s*(?:ደራሲ|ጸሐፊ|ፀሐፊ)\s*(?:{sep})(.+?)(?:\n|$)',
        # ደራሲ፦... without emoji
        rf'(?:ደራሲ|ጸሐፊ|ፀሐፊ)\s*(?:{sep})(.+?)(?:\n|$)',
        # Pen emoji patterns
        r'✍️\s*(.+?)(?:\n|$)',
        r'✍\s*(.+?)(?:\n|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, caption)
        if match:
            author = match.group(1).strip()
            # Remove trailing emojis and anything after them (e.g. 🗣ተርጓሚ line noise)
            author = re.sub(r'\s*[📚📖🔥✨💡⭐️🙏🗣💾📑📔👤]+.*$', '', author).strip()
            if author:
                return author

    return "Unknown"


def extract_title_from_caption(caption, file_name):
    """
    Extract title from Amharic caption patterns.
    Handles separators: ፦  :-  :  -  –  —
    Handles emoji prefixes: 📔, 📚
    
    Examples:
        📔ርዕስ:-መስቀሉን ማኮሰስ ፣ ስቅሉን ማራከስ
        📔ርዕስ፦ወቅታዊ ዘላለማዊ
        📔ርዕስ፦የዓለማችን ሁኔታዎችና የመጽሐፍ ቅዱስ ትንቢቶች
    """
    if not caption:
        return clean_filename(file_name)

    # Unified separator group
    sep = r'[:：፦]\s*|\s*:-\s*|\s*[–—]\s*'

    patterns = [
        # 📔ርዕስ፦... or 📔ርዕስ:-... (emoji glued to keyword)
        rf'📔\s*ርዕስ\s*(?:{sep})(.+?)(?:\n|$)',
        # ርዕስ፦... without emoji
        rf'ርዕስ\s*(?:{sep})(.+?)(?:\n|$)',
        # መጽሐፍ ስም:... 
        rf'መጽሐፍ\s*(?:ስም)?\s*(?:{sep})(.+?)(?:\n|$)',
        # 📚 ... (emoji followed by title text)
        r'📚\s*(.+?)(?:\n|$)',
    ]

    for pattern in patterns:
        match = re.search(pattern, caption)
        if match:
            title = match.group(1).strip()
            # Remove trailing emojis
            title = re.sub(r'\s*[📚📖🔥✨💡⭐️🙏🗣💾📑📔👤]+.*$', '', title).strip()
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
        # Amharic keywords
        "መጽሐፍ ቅዱስ": "መጽሐፍ ቅዱስ ጥናት",     # Bible Study
        "ጸሎት": "ጸሎት",                      # Prayer
        "ስብከት": "ስብከት",                    # Sermons
        "ነገረ መለኮት": "ነገረ መለኮት",           # Theology
        "ታሪክ": "የቤተክርስቲያን ታሪክ",          # Church History
        "ወንጌል": "ወንጌል",                    # Gospel
        "እምነት": "እምነት",                    # Faith
        "ጥምቀት": "ጥምቀት",                   # Baptism
        "ትምህርት": "ትምህርት",                 # Teaching/Doctrine
        "መዝሙር": "መዝሙር",                   # Hymns/Psalms
        "ክርስቲያናዊ": "ክርስቲያናዊ ሕይወት",      # Christian Living
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

        # Skip English-language books (handled by the English scraper)
        if is_english_book(caption):
            print(f"🔤 Skipping English book: {file_name}")
            skipped_count += 1
            continue

        # Extract metadata from caption early for accurate duplicate checking
        author = extract_author_from_caption(caption)
        title = extract_title_from_caption(caption, file_name)
        category = detect_amharic_category(f"{file_name} {caption}")
        date = message.date

        # Check if already exists (using the cleaned title to prevent duplicates)
        if book_exists(title):
            print(f"⏩ Skipping existing (Title Match): {title}")
            skipped_count += 1
            continue

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
