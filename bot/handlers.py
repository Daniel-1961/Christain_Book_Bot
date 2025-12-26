# bot/handlers.py
import sqlite3
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "books.db")

def get_books():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author, file_id FROM books LIMIT 30")
    rows = cursor.fetchall()
    conn.close()
    return rows

def build_books_keyboard(books):
    keyboard = [
        [InlineKeyboardButton(f"{title} ({author})", callback_data=str(book_id))]
        for book_id, title, author, _ in books
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    books = get_books()
    if not books:
        await update.message.reply_text("No books available yet.")
        return

    await update.message.reply_text(
        "📚 Welcome to the Christian Books Library\n\nSelect a book:",
        reply_markup=build_books_keyboard(books)
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 Christian Books Bot\n\n"
        "A curated library of Reformed and Christian resources.\n"
        "Authors: Calvin, Spurgeon, Owen, Sproul, and more."
    )

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    book_id = query.data

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_id FROM books WHERE id=?", (book_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        await query.message.reply_text("Book not found.")
        return

    title, file_id = row
    await query.message.reply_document(document=file_id, filename=title)
