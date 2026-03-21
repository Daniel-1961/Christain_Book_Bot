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
def get_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM books WHERE category IS NOT NULL")
    categories = [row[0] for row in cursor.fetchall()]
    conn.close()
    return categories


def get_authors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT author FROM books WHERE author IS NOT NULL")
    authors = [row[0] for row in cursor.fetchall()]
    conn.close()
    return authors


def get_books_by_category(category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, author, file_id FROM books WHERE category = ?",
        (category,),
    )
    books = cursor.fetchall()
    conn.close()
    return books


def get_books_by_author(author):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, author, file_id FROM books WHERE author = ?",
        (author,),
    )
    books = cursor.fetchall()
    conn.close()
    return books


def get_book_by_id(book_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_id FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book


def search_books(keyword):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, author FROM books WHERE title LIKE ? OR author LIKE ?",
        (f"%{keyword}%", f"%{keyword}%"),
    )
    results = cursor.fetchall()
    conn.close()
    return results


# -------------------------------
# UI Keyboards
# -------------------------------
def main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📚 Browse by Category", callback_data="menu_category")],
        [InlineKeyboardButton("👤 Browse by Author", callback_data="menu_author")],
        [InlineKeyboardButton("🔍 Search Books", callback_data="menu_search")],
        [InlineKeyboardButton("ℹ️ About", callback_data="menu_about")],
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
# Command Handlers
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Warm welcome and main menu."""
    welcome_text = (
        "🌿 *Welcome to Christian Books Bot!*\n\n"
        "Discover amazing spiritual resources from well-known reformed writers.\n"
        "You can browse books by category, author, or search by keywords.\n\n"
        "Choose an option below to get started:"
    )
    await update.message.reply_text(
        welcome_text, parse_mode="Markdown", reply_markup=main_menu_keyboard()
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
        "Our desire is to help you:\n"
        "• 📚 Discover classic works of theology, devotion, and church history\n"
        "• 🔍 Browse by author or category\n"
        "• 🙏 Deepen your understanding of Scripture and sound doctrine\n\n"
        "New books and improvements are being added regularly to make your experience smoother and richer over time.\n\n"
        "_May these resources encourage you to know Christ more deeply and to grow in grace and truth._\n\n"
        "💡 *Note from the Developer:*\n"
        "This project is continually improving to include more books, categories, and better user experience.\n\n"
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
    results = search_books(keyword)

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

    # Main menu
    if data == "menu_main":
        await query.message.edit_text(
            "🏠 Main Menu:", reply_markup=main_menu_keyboard()
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
            "Here, you'll find a growing collection of *Reformed and Evangelical writings*, organized by *author*, *category*, and *topic* — from the early Church Fathers to today's faithful teachers.\n\n"
            "Our desire is to help you:\n"
            "• 📚 Discover classic works of theology, devotion, and church history\n"
            "• 🔍 Browse by author or category\n"
            "• 🙏 Deepen your understanding of Scripture and sound doctrine\n\n"
            "New books and improvements are being added regularly to make your experience smoother and richer over time.\n\n"
            "_May these resources encourage you to know Christ more deeply and to grow in grace and truth._\n\n"
            "💡 *Note from the Developer:*\n"
            "This project is continually improving to include more books, categories, and better user experience.\n\n"
            "Enjoy your spiritual reading journey! ✨"
        )
        await query.message.reply_text(
            about_text, parse_mode="Markdown", reply_markup=about_keyboard()
        )
        return

    # Search
    if data == "menu_search":
        await query.message.reply_text(
            "🔍 To search for a book, use the command:\n`/search <keyword>`",
            parse_mode="Markdown",
            reply_markup=back_to_main_keyboard(),
        )
        return

    # Browse by category
    if data == "menu_category":
        categories = get_categories()
        if not categories:
            await query.message.edit_text(
                "No categories found.", reply_markup=back_to_main_keyboard()
            )
            return

        keyboard = [
            [InlineKeyboardButton(cat, callback_data=f"cat_{cat}")]
            for cat in categories
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
        await query.message.edit_text(
            "📚 Choose a category:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Browse by author
    if data == "menu_author":
        authors = get_authors()
        if not authors:
            await query.message.edit_text(
                "No authors found.", reply_markup=back_to_main_keyboard()
            )
            return

        keyboard = [
            [InlineKeyboardButton(auth, callback_data=f"auth_{auth}")]
            for auth in authors
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])
        await query.message.edit_text(
            "👤 Choose an author:", reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Category books
    if data.startswith("cat_"):
        category = data.replace("cat_", "")
        books = get_books_by_category(category)
        if not books:
            await query.message.edit_text(
                f"No books found in {category}.",
                reply_markup=back_to_main_keyboard(),
            )
            return

        keyboard = [
            [InlineKeyboardButton(f"{title} ({author})", callback_data=str(book_id))]
            for book_id, title, author, _ in books
        ]
        keyboard.append(
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_category")]
        )
        await query.message.edit_text(
            f"📖 Books in '{category}':",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # Author books
    if data.startswith("auth_"):
        author = data.replace("auth_", "")
        books = get_books_by_author(author)
        if not books:
            await query.message.edit_text(
                f"No books found by {author}.",
                reply_markup=back_to_main_keyboard(),
            )
            return

        keyboard = [
            [InlineKeyboardButton(title, callback_data=str(book_id))]
            for book_id, title, _, _ in books
        ]
        keyboard.append(
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_author")]
        )
        await query.message.edit_text(
            f"📚 Books by '{author}':",
            reply_markup=InlineKeyboardMarkup(keyboard),
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
