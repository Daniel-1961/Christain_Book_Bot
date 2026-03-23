# bot/handlers.py
import logging
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
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
            "SELECT MIN(id), category FROM books WHERE category IS NOT NULL AND category != '' AND language = ? GROUP BY category ORDER BY category",
            (language,))
    else:
        cursor.execute("SELECT MIN(id), category FROM books WHERE category IS NOT NULL AND category != '' GROUP BY category ORDER BY category")
    categories = cursor.fetchall()
    conn.close()
    return categories


def get_authors(language=None):
    conn = _get_conn()
    cursor = conn.cursor()
    if language:
        cursor.execute(
            "SELECT MIN(id), author FROM books WHERE author IS NOT NULL AND author != '' AND language = ? GROUP BY author ORDER BY author",
            (language,))
    else:
        cursor.execute("SELECT MIN(id), author FROM books WHERE author IS NOT NULL AND author != '' GROUP BY author ORDER BY author")
    authors = cursor.fetchall()
    conn.close()
    return authors


def get_book_metadata_by_id(book_id):
    """Helper to fetch category/author from a book ID (used to bypass callback limits)."""
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT category, author FROM books WHERE id=?", (book_id,))
    res = cursor.fetchone()
    conn.close()
    return res


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
            [InlineKeyboardButton("🌟 ቦቱን ደግፉ (Donate)", callback_data="menu_donate")],
            [InlineKeyboardButton("🔄 ቋንቋ ቀይር", callback_data="menu_change_lang")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("📚 Browse by Category", callback_data="menu_category")],
            [InlineKeyboardButton("👤 Browse by Author", callback_data="menu_author")],
            [InlineKeyboardButton("🔍 Search Books", callback_data="menu_search")],
            [InlineKeyboardButton("ℹ️ About", callback_data="menu_about")],
            [InlineKeyboardButton("🌟 Support Bot (Donate)", callback_data="menu_donate")],
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
    
    welcome_text = (
        "🌿 *Welcome to Christian Books Bot!*\n\n"
        "This bot provides easy access to a vast collection of timeless Christian books, sermons, and spiritual resources.\n"
        "You can browse by category, search by author, or find specific titles to help you grow in your faith.\n\n"
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
        "*Credits / Sources:*\n"
        "A special thanks to the following Telegram channels where these resources are gathered:\n"
        "🇬🇧 English: `@christiangoodbooks`\n"
        "🇪🇹 Amharic: `@amharicspritualbooks`\n\n"
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
        for book_id, title, author in results[:90] # Truncate to avoid 100 button limit error
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
            text = "🏠 ዋና ማዉጫ:"
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
            "*Credits / Sources:*\n"
            "A special thanks to the following Telegram channels where these resources are gathered:\n"
            "🇬🇧 English: `@christiangoodbooks`\n"
            "🇪🇹 Amharic: `@amharicspritualbooks`\n\n"
            "_May these resources encourage you to know Christ more deeply and to grow in grace and truth._\n\n"
            "Enjoy your spiritual reading journey! ✨"
        )
        await query.message.edit_text(
            about_text, parse_mode="Markdown", reply_markup=about_keyboard()
        )
        return

    # Support / Donate Options
    if data == "menu_donate":
        keyboard = [
            [InlineKeyboardButton("⭐️ 50 Stars (~$1)", callback_data="stars_50")],
            [InlineKeyboardButton("⭐️ 100 Stars (~$2)", callback_data="stars_100")],
            [InlineKeyboardButton("⭐️ 250 Stars (~$5)", callback_data="stars_250")],
            [InlineKeyboardButton("⬅️ Back", callback_data="menu_main")]
        ]
        text = (
            "🌟 *Support Christian Books Bot*\n\n"
            "This bot is free to use! If it has blessed you, please consider donating a few Telegram Stars to keep our server running and support new features.\n\n"
            "Choose an amount to donate securely via Telegram:"
        ) if language == "English" else (
            "🌟 *ለክርስቲያን መጽሐፍት ቦት ድጋፍ ያድርጉ*\n\n"
            "ይህ ቦት ነፃ ነው! ከተጠቀሙበትና ከተባረኩበት፣ ሰርቨር ለማሳደግና አዳዲስ ነገሮችን ለመጨመር በቴሌግራም ስታር አነስተኛ ድጋፍ ቢያደርጉልን እናመሰግናለን።\n\n"
            "በቴሌግራም የሚለገሱበትን መጠን ይምረጡ:"
        )
        await query.message.edit_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Send Star Invoice
    if data.startswith("stars_"):
        amount = int(data.split("_")[1])
        title = "Support Christian Books Bot"
        description = f"Thank you for supporting the hosting and maintenance of this bot with {amount} Stars! May God bless you."
        payload = "support_donation"
        currency = "XTR"  # Telegram Stars native currency
        prices = [LabeledPrice("Donation", amount)]
        
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token="",  # Must be empty for Stars
            currency=currency,
            prices=prices
        )
        return

    # Search
    if data == "menu_search":
        if language == "Amharic":
            text = "🔍 መጽሐፍ ለመፈለግ ይህን ትእዛዝ ይጠቀሙ:\n`/search <ቁልፍ ቃል>`"
        else:
            text = "🔍 To search for a book, use the command:\n`/search <keyword>`"
        await query.message.edit_text(
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
            [InlineKeyboardButton(cat, callback_data=f"cat_{book_id}")]
            for book_id, cat in categories[:90]
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
            [InlineKeyboardButton(auth, callback_data=f"auth_{book_id}")]
            for book_id, auth in authors[:90]
        ]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="menu_main")])

        title = "👤 ደራሲ ይምረጡ:" if language == "Amharic" else "👤 Choose an author:"
        await query.message.edit_text(
            title, reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Category books
    if data.startswith("cat_"):
        ref_id = data.replace("cat_", "")
        metadata = get_book_metadata_by_id(ref_id)
        if not metadata: return
        category = metadata[0]

        books = get_books_by_category(category, language)
        if not books:
            msg = f"በ{category} ውስጥ መጽሐፍ አልተገኘም።" if language == "Amharic" else f"No books found in {category}."
            await query.message.edit_text(msg, reply_markup=back_to_main_keyboard())
            return

        keyboard = [
            [InlineKeyboardButton(f"{title} ({author})", callback_data=str(book_id))]
            for book_id, title, author, _ in books[:90]
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
        ref_id = data.replace("auth_", "")
        metadata = get_book_metadata_by_id(ref_id)
        if not metadata: return
        author = metadata[1]
        
        books = get_books_by_author(author, language)
        if not books:
            msg = f"በ{author} የተጻፉ መጽሐፍት አልተገኙም።" if language == "Amharic" else f"No books found by {author}."
            await query.message.edit_text(msg, reply_markup=back_to_main_keyboard())
            return

        keyboard = [
            [InlineKeyboardButton(title, callback_data=str(book_id))]
            for book_id, title, _, _ in books[:90]
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
        await query.answer("❌ Book not found.", show_alert=True)
        return

    title, message_id = book
    if message_id:
        try:
            await context.bot.copy_message(
                chat_id=update.effective_chat.id,
                from_chat_id=int(os.getenv("ARCHIVE_CHAT_ID")),
                message_id=int(message_id),
            )
            # Acknowledge the click without spamming the chat
            await query.answer(f"Sent: {title}")
        except Exception as e:
            logger.error(f"Copy message failed: {e}")
            await query.answer("❌ Failed to send the book.", show_alert=True)
    else:
        await query.answer("❌ File not available for download.", show_alert=True)

# -------------------------------
# Payment Handlers
# -------------------------------
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Answers the PreCheckoutQuery for Telegram Stars"""
    query = update.pre_checkout_query
    if query.invoice_payload != 'support_donation':
        await query.answer(ok=False, error_message="Something went wrong with the payload.")
    else:
        await query.answer(ok=True)


async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirms the successful Star payment and thanks the user."""
    await update.message.reply_text(
        "🎉 *God bless you!*\n\nThank you so much for your generous support! Your contribution helps keep this bot alive and free for everyone.",
        parse_mode="Markdown"
    )
