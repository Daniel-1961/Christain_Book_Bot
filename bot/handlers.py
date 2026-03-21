# bot/handlers.py
import logging
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from dotenv import load_dotenv

load_dotenv()

# Database settings
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "books.db")

# Logging
logger = logging.getLogger(__name__)


# -------------------------------
# Database Helpers
# -------------------------------
def _get_conn():
    return sqlite3.connect(DB_PATH)


def get_categories(language=None):
    conn = _get_conn()
    cursor = conn.cursor()
    if language:
        cursor.execute(
            "SELECT DISTINCT category FROM books WHERE category IS NOT NULL AND language = ? ORDER BY category",
            (language,))
    else:
        cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL ORDER BY category")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories


def get_authors(language=None):
    conn = _get_conn()
    cursor = conn.cursor()
    if language:
        cursor.execute(
            "SELECT DISTINCT author FROM books WHERE author IS NOT NULL AND language = ? ORDER BY author",
            (language,))
    else:
        cursor.execute("SELECT DISTINCT author FROM books WHERE author IS NOT NULL ORDER BY author")
    authors = [row[0] for row in cursor.fetchall()]
    conn.close()
    return authors


def get_books_by_category(category, language=None):
    conn = _get_conn()
    cursor = conn.cursor()
    if language:
        cursor.execute(
            "SELECT id, title, author, file_id FROM books WHERE category = ? AND language = ?",
            (category, language))
    else:
        cursor.execute(
            "SELECT id, title, author, file_id FROM books WHERE category = ?",
            (category,))
    books = cursor.fetchall()
    conn.close()
    return books


def get_books_by_author(author, language=None):
    conn = _get_conn()
    cursor = conn.cursor()
    if language:
        cursor.execute(
            "SELECT id, title, author, file_id FROM books WHERE author = ? AND language = ?",
            (author, language))
    else:
        cursor.execute(
            "SELECT id, title, author, file_id FROM books WHERE author = ?",
            (author,))
    books = cursor.fetchall()
    conn.close()
    return books


def get_book_by_id(book_id):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_id FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book


def search_books(keyword, language=None):
    conn = _get_conn()
    cursor = conn.cursor()
    if language:
        cursor.execute(
            "SELECT id, title, author FROM books WHERE (title LIKE ? OR author LIKE ?) AND language = ?",
            (f"%{keyword}%", f"%{keyword}%", language))
    else:
        cursor.execute(
            "SELECT id, title, author FROM books WHERE title LIKE ? OR author LIKE ?",
            (f"%{keyword}%", f"%{keyword}%"))
    results = cursor.fetchall()
    conn.close()
    return results


def record_user(user_id, username=None, first_name=None):
    """Record user on first visit."""
    from datetime import datetime
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at) VALUES (?, ?, ?, ?)",
        (user_id, username, first_name, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_monthly_user_count():
    from datetime import datetime
    conn = _get_conn()
    cursor = conn.cursor()
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    cursor.execute("SELECT COUNT(*) FROM users WHERE joined_at >= ?", (month_start,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_user_count():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# -------------------------------
# UI Keyboards
# -------------------------------
def language_selection_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_English"),
            InlineKeyboardButton("🇪🇹 አማርኛ", callback_data="lang_Amharic"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def main_menu_keyboard(language="English"):
    if language == "Amharic":
        keyboard = [
            [InlineKeyboardButton("📚 በምድብ ፈልግ", callback_data="menu_category")],
            [InlineKeyboardButton("👤 በደራሲ ፈልግ", callback_data="menu_author")],
            [InlineKeyboardButton("🔍 መጽሐፍ ፈልግ", callback_data="menu_search")],
            [InlineKeyboardButton("ℹ️ ስለ ቦቱ", callback_data="menu_about")],
            [InlineKeyboardButton("🔄 ቋንቋ ቀይር", callback_data="menu_change_lang")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📚 Browse by Category", callback_data="menu_category")],
            [InlineKeyboardButton("👤 Browse by Author", callback_data="menu_author")],
            [InlineKeyboardButton("🔍 Search Books", callback_data="menu_search")],
            [InlineKeyboardButton("ℹ️ About", callback_data="menu_about")],
            [InlineKeyboardButton("🔄 Change Language", callback_data="menu_change_lang")],
        ]
    return InlineKeyboardMarkup(keyboard)


def back_to_main_keyboard():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="menu_main")]]
    )


def about_keyboard():
    keyboard = [
        [InlineKeyboardButton("📩 Contact Admin", url="https://t.me/Dani1961")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


# -------------------------------
# Helper: Get user's language
# -------------------------------
def get_user_language(context):
    return context.user_data.get("language", None)


def set_user_language(context, language):
    context.user_data["language"] = language


# -------------------------------
# Command Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome message with language selection."""
    user = update.effective_user
    record_user(user.id, user.username, user.first_name)

    total_users = get_total_user_count()
    monthly_users = get_monthly_user_count()

    welcome_text = (
        "🌿 *Welcome to Christian Books Bot!*\n"
        f"👥 {total_users} total users • {monthly_users} this month\n\n"
        "Choose your language / ቋንቋዎን ይምረጡ:"
    )
    await update.message.reply_text(
        welcome_text, parse_mode="Markdown", reply_markup=language_selection_keyboard()
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """About the bot."""
    about_text = (
        '📖 *"For I am not ashamed of the gospel, for it is the power of God for salvation '
        'to everyone who believes."*\n'
        "_— Romans 1:16_\n\n"
        " *About Christian Books Bot*\n\n"
        "This bot was created with a simple purpose — *to make timeless Christian books and resources easily accessible* to everyone.\n\n"
        "Here, you'll find a growing collection of *Reformed and Evangelical writings*, organized by *author*, *category*, and *topic* — from the early Church Fathers to today's faithful teachers.\n\n"
        "🇪🇹 *The bot also provides Amharic spiritual resources!*\n\n"
        "Our desire is to help you:\n"
        "• 📚 Discover classic works of theology, devotion, and church history\n"
        "• 🔍 Browse by author or category\n"
        "• 🙏 Deepen your understanding of Scripture and sound doctrine\n\n"
        "_May these resources encourage you to know Christ more deeply and to grow in grace and truth._\n\n"
        "Enjoy your spiritual reading journey! ✨"
    )
    await update.message.reply_text(
        about_text, parse_mode="Markdown", reply_markup=about_keyboard()
    )


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search for books using /search <keyword>."""
    if len(context.args) == 0:
        await update.message.reply_text(
            "Usage: `/search <keyword>`", parse_mode="Markdown"
        )
        return

    keyword = " ".join(context.args)
    language = get_user_language(context)
    results = search_books(keyword, language)

    if not results:
        await update.message.reply_text(f"❌ No books found for: {keyword}")
        return

    keyboard = [
        [InlineKeyboardButton(f"{title} ({author})", callback_data=str(book_id))]
        for book_id, title, author in results
    ]
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])

    await update.message.reply_text(
        f"🔍 Search results for '{keyword}':",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# -------------------------------
# Callback Handler
# -------------------------------
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Language selection
    if data.startswith("lang_"):
        language = data.replace("lang_", "")
        set_user_language(context, language)

        if language == "Amharic":
            text = "🇪🇹 *አማርኛ ተመርጧል!*\n\nከዚህ በታች ያሉትን ምረጡ:"
        else:
            text = "🇬🇧 *English selected!*\n\nChoose an option below:"

        await query.message.edit_text(
            text, parse_mode="Markdown", reply_markup=main_menu_keyboard(language)
        )
        return

    # Change language
    if data == "menu_change_lang":
        await query.message.edit_text(
            "Choose your language / ቋንቋዎን ይምረጡ:",
            reply_markup=language_selection_keyboard()
        )
        return

    # Get current language
    language = get_user_language(context) or "English"

    # Main menu
    if data == "menu_main":
        if language == "Amharic":
            text = "🏠 ዋና ምናሌ:"
        else:
            text = "🏠 Main Menu:"
        await query.message.edit_text(
            text, reply_markup=main_menu_keyboard(language)
        )
        return

    # About
    if data == "menu_about":
        about_text = (
            '📖 *"For I am not ashamed of the gospel, for it is the power of God for salvation '
            'to everyone who believes."*\n'
            "_— Romans 1:16_\n\n"
            "🌿 *About Christian Books Bot*\n\n"
            "This bot was created with a simple purpose — *to make timeless Christian books and resources easily accessible* to everyone.\n\n"
            "Here, you'll find a growing collection of *Reformed and Evangelical writings*, organized by *author*, *category*, and *topic*.\n\n"
            "🇪🇹 *The bot also provides Amharic spiritual resources!*\n\n"
            "Our desire is to help you:\n"
            "• 📚 Discover classic works of theology, devotion, and church history\n"
            "• 🔍 Browse by author or category\n"
            "• 🙏 Deepen your understanding of Scripture and sound doctrine\n\n"
            "_May these resources encourage you to know Christ more deeply and to grow in grace and truth._\n\n"
            "Enjoy your spiritual reading journey! ✨"
        )
        await query.message.reply_text(
            about_text, parse_mode="Markdown", reply_markup=about_keyboard()
        )
        return

    # Search
    if data == "menu_search":
        if language == "Amharic":
            text = "🔍 መጽሐፍ ለመፈለግ ይህን ትእዛዝ ይጠቀሙ:\n`/search <ቁልፍ ቃል>`"
        else:
            text = "🔍 To search for a book, use the command:\n`/search <keyword>`"
        await query.message.reply_text(
            text,
            parse_mode="Markdown",
            reply_markup=back_to_main_keyboard(),
        )
        return

    # Browse by category
    if data == "menu_category":
        categories = get_categories(language)
        if not categories:
            msg = "ምድቦች አልተገኙም።" if language == "Amharic" else "No categories found."
            await query.message.edit_text(msg, reply_markup=back_to_main_keyboard())
            return

        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"cat_{cat}")]
            for cat in categories
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])

        title = "📚 ምድብ ይምረጡ:" if language == "Amharic" else "📚 Choose a category:"
        await query.message.edit_text(
            title, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Browse by author
    if data == "menu_author":
        authors = get_authors(language)
        if not authors:
            msg = "ደራሲዎች አልተገኙም።" if language == "Amharic" else "No authors found."
            await query.message.edit_text(msg, reply_markup=back_to_main_keyboard())
            return

        keyboard = [
            [InlineKeyboardButton(auth, callback_data=f"auth_{auth}")]
            for auth in authors
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])

        title = "👤 ደራሲ ይምረጡ:" if language == "Amharic" else "👤 Choose an author:"
        await query.message.edit_text(
            title, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Category books
    if data.startswith("cat_"):
        category = data.replace("cat_", "")
        books = get_books_by_category(category, language)
        if not books:
            msg = f"በ{category} ውስጥ መጽሐፍ አልተገኘም።" if language == "Amharic" else f"No books found in {category}."
            await query.message.edit_text(msg, reply_markup=back_to_main_keyboard())
            return

        keyboard = [
            [InlineKeyboardButton(f"{title} ({author})", callback_data=str(book_id))]
            for book_id, title, author, _ in books
        ]
        keyboard.append(
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_category")]
        )

        header = f"📖 '{category}' ምድብ:" if language == "Amharic" else f"📖 Books in '{category}':"
        await query.message.edit_text(
            header, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Author books
    if data.startswith("auth_"):
        author = data.replace("auth_", "")
        books = get_books_by_author(author, language)
        if not books:
            msg = f"በ{author} የተጻፉ መጽሐፍት አልተገኙም።" if language == "Amharic" else f"No books found by {author}."
            await query.message.edit_text(msg, reply_markup=back_to_main_keyboard())
            return

        keyboard = [
            [InlineKeyboardButton(title, callback_data=str(book_id))]
            for book_id, title, _, _ in books
        ]
        keyboard.append(
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_author")]
        )

        header = f"📚 የ{author} መጽሐፍት:" if language == "Amharic" else f"📚 Books by '{author}':"
        await query.message.edit_text(
            header, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Book download
    book = get_book_by_id(data)
    if not book:
        await query.message.reply_text("Book not found.")
        return

    title, message_id = book
    if message_id:
        try:
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=int(os.getenv("ARCHIVE_CHAT_ID")),
                message_id=int(message_id),
            )
        except Exception as e:
            await query.message.reply_text(f"❌ Failed to send the book: {e}")
    else:
        await query.message.reply_text("File not available for download.")
