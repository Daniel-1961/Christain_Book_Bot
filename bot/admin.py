# bot/admin.py
import logging
import asyncio
import os
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    filters
)

from database.db import get_total_user_count, get_monthly_user_count, get_all_users, insert_book, book_exists

# Configuration
ADMIN_ID = 1001572729
ARCHIVE_CHAT_ID = int(os.getenv("ARCHIVE_CHAT_ID", "-1")) # Ensure fallback doesn't crash, but it should be in env or WSGI

logger = logging.getLogger(__name__)

# Conversation states for Book Uploader
WAITING_FOR_FILE, WAITING_FOR_LANGUAGE, WAITING_FOR_TITLE, WAITING_FOR_AUTHOR, WAITING_FOR_CATEGORY = range(5)

# -------------------------------
# Admin Authenticator Helper
# -------------------------------
def is_admin(update: Update) -> bool:
    return update.effective_user.id == ADMIN_ID


# -------------------------------
# 1. Enhanced Admin /stats Command
# -------------------------------
async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    total_users = get_total_user_count()
    monthly_users = get_monthly_user_count()
    
    # Get book statistics
    import sqlite3
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM books")
    total_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books WHERE language='English'")
    english_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM books WHERE language='Amharic'")
    amharic_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT category) FROM books WHERE category IS NOT NULL AND category != ''")
    total_categories = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT author) FROM books WHERE author IS NOT NULL AND author != ''")
    total_authors = cursor.fetchone()[0]
    
    # Get recent activity (last 7 days)
    cursor.execute("""
        SELECT COUNT(*) FROM users 
        WHERE joined_at >= datetime('now', '-7 days')
    """)
    weekly_users = cursor.fetchone()[0]
    
    conn.close()
    
    stats_text = (
        "🔐 *Admin Panel - Detailed Statistics*\n\n"
        "*👥 User Metrics:*\n"
        f"• Total Users: *{total_users:,}*\n"
        f"• This Month: *{monthly_users:,}* 📅\n"
        f"• Last 7 Days: *{weekly_users:,}* 📊\n\n"
        "*📚 Library Metrics:*\n"
        f"• Total Books: *{total_books:,}*\n"
        f"• English: *{english_books:,}* 🇬🇧\n"
        f"• Amharic: *{amharic_books:,}* 🇪🇹\n\n"
        "*📖 Content Metrics:*\n"
        f"• Categories: *{total_categories}*\n"
        f"• Authors: *{total_authors}*\n\n"
        "*🛠️ Admin Commands:*\n"
        "• `/broadcast <msg>` - Send message to all users\n"
        "• `/stats` - View statistics\n"
        "• `/export` - Export user list\n"
        "• `/pending` - View pending book submissions\n"
        "• Send PDF/EPUB - Add book manually\n\n"
        "_Statistics updated in real-time_"
    )
    
    await update.message.reply_text(stats_text, parse_mode="Markdown")


# -------------------------------
# 2. /broadcast Command
# -------------------------------
def _broadcast_thread(bot, users, message, admin_id):
    """Runs the broadcast loop in a completely separate OS thread so the Webhook worker doesn't freeze."""
    async def background_task():
        success = 0
        failed = 0
        for user_id in users:
            try:
                await bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown", disable_web_page_preview=True)
                success += 1
                await asyncio.sleep(0.05)  # 50ms sleep strictly enforced by Telegram limits
            except Exception as e:
                logger.error(f"Failed to send broadcast to {user_id}: {e}")
                failed += 1

        try:
            await bot.send_message(
                chat_id=admin_id, 
                text=f"✅ *Broadcast Complete!*\n\nDelivered: {success}\nFailed: {failed}", 
                parse_mode="Markdown"
            )
        except Exception:
            pass

    # Create a new event loop for this specific background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(background_task())
    loop.close()


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return

    message = update.message.text.replace("/broadcast", "").strip()
    
    if not message:
        await update.message.reply_text("⚠️ Usage: `/broadcast <your message here>`", parse_mode="Markdown")
        return

    users = get_all_users()
    if not users:
        await update.message.reply_text("No users found in the database.")
        return

    # Reply immediately so the PythonAnywhere web worker is freed up!
    await update.message.reply_text(f"🚀 *Started broadcast to {len(users)} users...*\nSince you are on a free tier, this is running in the background. You'll get a confirmation message when it's done.", parse_mode="Markdown")

    # Fire and forget the thread
    thread = threading.Thread(target=_broadcast_thread, args=(context.bot, users, message, update.effective_user.id))
    thread.daemon = True
    thread.start()


# -------------------------------
# 3. /export Command - Export Users List
# -------------------------------
async def export_users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Export user list as CSV file"""
    if not is_admin(update):
        return
    
    await update.message.reply_text("📊 Generating user export...")
    
    try:
        import sqlite3
        import csv
        import io
        
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id, username, first_name, joined_at 
            FROM users 
            ORDER BY joined_at DESC
        """)
        users = cursor.fetchall()
        conn.close()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['User ID', 'Username', 'First Name', 'Joined At'])
        
        for user in users:
            writer.writerow(user)
        
        # Send as file
        csv_data = output.getvalue().encode('utf-8')
        await update.message.reply_document(
            document=csv_data,
            filename=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            caption=f"📊 *User Export*\n\nTotal Users: {len(users)}\nExported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        await update.message.reply_text(f"❌ Export failed: {str(e)}")


# -------------------------------
# 4. /pending Command - View Pending Book Contributions
# -------------------------------
async def pending_books_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View and manage pending book submissions from users"""
    if not is_admin(update):
        return
    
    try:
        import sqlite3
        
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if pending_books table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='pending_books'
        """)
        
        if not cursor.fetchone():
            await update.message.reply_text(
                "ℹ️ No pending submissions table found.\n\n"
                "User contributions are not enabled yet."
            )
            conn.close()
            return
        
        cursor.execute("""
            SELECT id, user_id, title, author, category, language, submitted_at 
            FROM pending_books 
            WHERE status='pending' 
            ORDER BY submitted_at DESC 
            LIMIT 10
        """)
        pending = cursor.fetchall()
        conn.close()
        
        if not pending:
            await update.message.reply_text("✅ No pending book submissions!")
            return
        
        # Format pending books
        text = f"📋 *Pending Book Submissions* ({len(pending)})\n\n"
        
        for book in pending:
            book_id, user_id, title, author, category, language, submitted_at = book
            text += (
                f"*ID:* `{book_id}`\n"
                f"📖 {title}\n"
                f"👤 {author}\n"
                f"📚 {category} | {language}\n"
                f"👥 User: `{user_id}`\n"
                f"📅 {submitted_at[:10]}\n\n"
            )
        
        text += (
            "\n*To approve:* `/approve <id>`\n"
            "*To reject:* `/reject <id>`"
        )
        
        await update.message.reply_text(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Failed to get pending books: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")


# -------------------------------
# 3. /cancel Command (for uploader)
# -------------------------------
async def cancel_add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update):
        return ConversationHandler.END
    await update.message.reply_text("❌ Book upload cancelled.")
    context.user_data.clear()
    return ConversationHandler.END


# -------------------------------
# 4. conversational manual uploader
# -------------------------------
async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Triggered when admin sends a document."""
    if not is_admin(update):
        return ConversationHandler.END

    document = update.message.document
    if not document:
        await update.message.reply_text("Please send a valid file (PDF/EPUB) or /cancel.")
        return WAITING_FOR_FILE

    # Cache message ID for forwarding later
    context.user_data["book_message_id"] = update.message.id
    context.user_data["mime_type"] = document.mime_type

    keyboard = [
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="add_lang_English"),
            InlineKeyboardButton("🇪🇹 Amharic", callback_data="add_lang_Amharic")
        ]
    ]
    await update.message.reply_text(
        "📄 File received! What is the language of this book?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_FOR_LANGUAGE


async def receive_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    language = query.data.split("_")[-1]
    context.user_data["language"] = language
    
    await query.edit_message_text(f"Language set to: *{language}*\n\nPlease type the *Title* of the book:", parse_mode="Markdown")
    return WAITING_FOR_TITLE


async def receive_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    title = update.message.text
    context.user_data["title"] = title
    
    await update.message.reply_text(f"Title set to: *{title}*\n\nPlease type the *Author* of the book:", parse_mode="Markdown")
    return WAITING_FOR_AUTHOR


async def receive_author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    author = update.message.text
    context.user_data["author"] = author
    
    await update.message.reply_text(
        f"Author set to: *{author}*\n\nFinally, type the *Category* for this book (e.g. 'ጸሎት', 'Theology', 'ስብከት'):", 
        parse_mode="Markdown"
    )
    return WAITING_FOR_CATEGORY


async def receive_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = update.message.text
    
    if not category:
        await update.message.reply_text("Please type a valid category name.")
        return WAITING_FOR_CATEGORY

    # Everything gathered, let's insert to DB!
    await update.message.reply_text("⏳ Processing and saving book...")

    try:
        # First, forward the file to the archive channel to get a fresh message_id
        forwarded = await context.bot.forward_message(
            chat_id=ARCHIVE_CHAT_ID,
            from_chat_id=update.effective_chat.id,
            message_id=context.user_data["book_message_id"]
        )
        
        # Save to database
        insert_book(
            title=context.user_data["title"],
            caption="",  # Manual uploads usually don't need the caption parsed
            author=context.user_data["author"],
            category=category,
            mime_type=context.user_data["mime_type"],
            file_id=str(forwarded.message_id),
            date=str(datetime.utcnow().date()),
            language=context.user_data["language"]
        )
        
        await update.message.reply_text(
            f"✅ *Book Successfully Added!*\n\n"
            f"📖 Title: {context.user_data['title']}\n"
            f"👤 Author: {context.user_data['author']}\n"
            f"📚 Category: {category}\n"
            f"🌐 Language: {context.user_data['language']}",
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Error saving manual book: {e}")
        await update.message.reply_text(f"❌ Failed to save book to archive/DB: {e}")

    # Clear state
    context.user_data.clear()
    return ConversationHandler.END


# Assemble the ConversationHandler
add_book_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Document.ALL, receive_file)],
    states={
        WAITING_FOR_FILE: [MessageHandler(filters.Document.ALL, receive_file)],
        WAITING_FOR_LANGUAGE: [CallbackQueryHandler(receive_language, pattern="^add_lang_")],
        WAITING_FOR_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_title)],
        WAITING_FOR_AUTHOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_author)],
        WAITING_FOR_CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_category)],
    },
    fallbacks=[CommandHandler("cancel", cancel_add_book)]
)
