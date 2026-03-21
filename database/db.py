# database/db.py
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')


# -------------------------------
# Book Operations
# -------------------------------
def insert_book(title, caption, author=None, category=None, tags=None,
                mime_type=None, file_id=None, file_path=None, date=None,
                language='English'):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, caption, author, category, tags, mime_type,
                           file_id, file_path, date, language)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, caption, author, category, tags, mime_type, file_id,
          file_path, date, language))
    conn.commit()
    conn.close()


def book_exists(title, file_id=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if file_id:
        cursor.execute("SELECT 1 FROM books WHERE title=? OR file_id=?",
                        (title, file_id))
    else:
        cursor.execute("SELECT 1 FROM books WHERE title=?", (title,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


# -------------------------------
# Language-aware Queries
# -------------------------------
def get_categories_by_language(language):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT DISTINCT category FROM books WHERE language = ? AND category IS NOT NULL ORDER BY category ASC',
        (language,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def get_authors_by_language(language):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT DISTINCT author FROM books WHERE language = ? AND author IS NOT NULL ORDER BY author ASC',
        (language,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def get_books_by_category_and_language(category, language):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, author, file_id FROM books WHERE category = ? AND language = ? ORDER BY title ASC',
        (category, language))
    books = cursor.fetchall()
    conn.close()
    return books


def get_books_by_author_and_language(author, language):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, author, file_id FROM books WHERE author = ? AND language = ? ORDER BY title ASC',
        (author, language))
    books = cursor.fetchall()
    conn.close()
    return books


def search_books_by_language(keyword, language):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, title, author FROM books WHERE (title LIKE ? OR author LIKE ?) AND language = ?',
        (f'%{keyword}%', f'%{keyword}%', language))
    results = cursor.fetchall()
    conn.close()
    return results


def get_book_by_id(book_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT title, file_id FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return book


# -------------------------------
# Legacy queries (backward compatible)
# -------------------------------
def get_all_books():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, caption, author, category, tags, mime_type, file_id, file_path, date FROM books')
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "caption": r[2], "author": r[3],
         "category": r[4], "tags": r[5], "mime_type": r[6], "file_id": r[7],
         "file_path": r[8], "date": r[9]}
        for r in rows
    ]


def get_all_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM books ORDER BY category ASC')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


def get_all_authors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT author FROM books ORDER BY author ASC')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]


# -------------------------------
# User Tracking
# -------------------------------
def record_user(user_id, username=None, first_name=None):
    """Record a user on first visit (INSERT OR IGNORE)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, joined_at)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_monthly_user_count():
    """Count unique users who joined in the current month."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE joined_at >= ?",
        (month_start,))
    count = cursor.fetchone()[0]
    conn.close()
    return count


def get_total_user_count():
    """Count all unique users."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count