# channel_scraper/scraper.py
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaDocument, DocumentAttributeFilename
import requests
import os
from dotenv import load_dotenv
from database.db import insert_book
from database.models import create_tables
from database.db import book_exists
import time
from telethon.errors import FloodWaitError


# -------------------------------
# 🔹 Load Environment Variables
# -------------------------------
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ARCHIVE_CHAT_ID= int(os.getenv("ARCHIVE_CHAT_ID"))

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
    "reformation": "Reformation",
    "spiritual": "Spiritual Growth",
    "gospel": "Gospel Studies",
    "discipleship": "Discipleship",
    "sola":"Sola"
}

AUTHOR_RULES = {
    # 🏛️ Early Church Fathers
    "augustine": "Augustine of Hippo",
    "athanasius": "Athanasius of Alexandria",
    "jerome": "Jerome",
    "chrysostom": "John Chrysostom",
    "ambrose": "Ambrose of Milan",
    "gregory": "Gregory the Great",
    "irenaues": "Irenaeus of Lyons",
    "tertullian": "Tertullian",
    "origen": "Origen of Alexandria",
    "clement": "Clement of Rome",

    # ⛪ Medieval & Scholastic Thinkers
    "anselm": "Anselm of Canterbury",
    "aquinas": "Thomas Aquinas",
    "bernard": "Bernard of Clairvaux",
    "bonaventure": "Bonaventure",
    "lombard": "Peter Lombard",
    "scotus": "John Duns Scotus",
    "ockham": "William of Ockham",
    "siena": "Catherine of Siena",
    "norwich": "Julian of Norwich",

    # 📜 Reformation Era
    "calvin": "John Calvin",
    "luther": "Martin Luther",
    "zwingli": "Ulrich Zwingli",
    "beza": "Theodore Beza",
    "knox": "John Knox",
    "bullinger": "Heinrich Bullinger",

    # 📖 Puritans & Post-Reformation Divines
    "perkins": "William Perkins",
    "sibbes": "Richard Sibbes",
    "goodwin": "Thomas Goodwin",
    "watson": "Thomas Watson",
    "brooks": "Thomas Brooks",
    "owen": "John Owen",
    "bunyan": "John Bunyan",
    "boston": "Thomas Boston",
    "brakel": "Wilhelmus à Brakel",
    "gill": "John Gill",
    "turretin": "Francis Turretin",
    "baxter": "Richard Baxter",
    "edwards": "Jonathan Edwards",

    # 🧠 19th–20th Century Reformed Theologians
    "spurgeon": "Charles H. Spurgeon",
    "warfield": "B.B. Warfield",
    "hodge": "Charles Hodge",
    "bavinck": "Herman Bavinck",
    "berkhof": "Louis Berkhof",
    "kuper": "Abraham Kuyper",
    "vos": "Geerhardus Vos",
    "murray": "John Murray",
    "lloyd": "Martyn Lloyd-Jones",
    "packer": "J.I. Packer",
    "stott": "John Stott",
    "sproul": "R.C. Sproul",
    "macarthur": "John MacArthur",
    "ferguson": "Sinclair Ferguson",
    "boice": "James Montgomery Boice",
    "pink": "A.W. Pink",
    "henry": "Matthew Henry",
    "hodge_a": "A.A. Hodge",
    "machen": "J. Gresham Machen",
    "van_til": "Cornelius Van Til",
    "frame": "John Frame",
    "horton": "Michael Horton",
    "beeke": "Joel Beeke",
    "dever": "Mark Dever",
    "ryle": "J.C. Ryle",

    # 📚 Modern Evangelical Scholars & Commentators
    "carson": "D.A. Carson",
    "moo": "Douglas Moo",
    "morris": "Leon Morris",
    "bruce": "F.F. Bruce",
    "fee": "Gordon Fee",
    "osborne": "Grant R. Osborne",
    "grudem": "Wayne Grudem",
    "wright": "N.T. Wright",
    "barclay": "William Barclay",
    "wiersbe": "Warren Wiersbe",  # "Be Series"
    "hughes": "R. Kent Hughes",
    "schreiner": "Thomas R. Schreiner",
    "powlison": "David Powlison",
    "tripp": "Paul David Tripp",
    "bridges": "Jerry Bridges",
    "newheiser": "Jim Newheiser",

    # 🔥 Contemporary Reformed & Evangelical Preachers
    "piper": "John Piper",
    "keller": "Tim Keller",
    "begg": "Alistair Begg",
    "lawson": "Steven J. Lawson",
    "deyoung": "Kevin DeYoung",
    "baucham": "Voddie Baucham",
    "washer": "Paul Washer",
    "justin_peters": "Justin Peters",
    "mbewe": "Conrad Mbewe",
    "chandler": "Matt Chandler",
    "macarthur_john": "John MacArthur",
    "sproul_rc": "R.C. Sproul",
    "sproul_jr": "R.C. Sproul Jr.",
    "reagan": "David Reagan",
    "phillips": "Richard Phillips",
    "moore": "Russell Moore",
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
    ]

    with client:
        print("📡 Scraping Telegram channel for Reformed books...")
        forwarded_count = 0
        skipped_count = 0

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
            if book_exists(file_name):
                print(f"⏩ Skipping already existing book: {file_name}")
                skipped_count += 1
                continue

            # Forward the message to your private channel
            try:
                forwarded = client.forward_messages(
                    ARCHIVE_CHAT_ID,
                    message.id,
                    from_peer=CHANNEL_USERNAME
                )
            except FloodWaitError as e:
                print(f"⏳ Flood wait: sleeping for {e.seconds} seconds...")
                time.sleep(e.seconds)
                # After sleeping, try again
                forwarded = client.forward_messages(
                    ARCHIVE_CHAT_ID,
                    message.id,
                    from_peer=CHANNEL_USERNAME
                )

            # Get message_id from forwarded message
            message_id = None
            if forwarded:
                if isinstance(forwarded, list):
                    message_id = forwarded[0].id
                else:
                    message_id = forwarded.id

            if not message_id:
                print(f"❌ Failed to forward {file_name}")
                continue

            # Store in DB (original caption, message_id, etc.)
            insert_book(
                title=file_name,
                caption=caption,
                author=author,
                category=category,
                mime_type=mime_type,
                file_id=str(message_id),
                date=str(date)
            )

            forwarded_count += 1
            print(f"✅ Forwarded {file_name} ({forwarded_count})")

        print(f"\n🎯 Finished forwarding and saving {forwarded_count} books!")
        print(f"⏩ Skipped {skipped_count} books already in database.")

# -------------------------------
# 🔹 Run Script
# -------------------------------
if __name__ == "__main__":
    scrape_channel(limit=5000)
