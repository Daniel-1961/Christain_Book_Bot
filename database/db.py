# database/db.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')

# Insert book
def insert_book(title, caption, author=None, category=None, tags=None, mime_type=None, file_id=None, file_path=None, date=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO books (title, caption, author, category, tags, mime_type, file_id, file_path, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, caption, author, category, tags, mime_type, file_id, file_path, date))
    conn.commit()
    conn.close()

# Fetch all books
def get_all_books():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, caption, author, category, tags, mime_type, file_id, file_path, date FROM books')
    rows = cursor.fetchall()
    conn.close()
    books = [
        {
            "id": row[0],
            "title": row[1],
            "caption": row[2],
            "author": row[3],
            "category": row[4],
            "tags": row[5],
            "mime_type": row[6],
            "file_id": row[7],
            "file_path": row[8],
            "date": row[9],
        } for row in rows
    ]
    return books

# Get unique categories
def get_all_categories():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT category FROM books ORDER BY category ASC')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

# Get unique authors
def get_all_authors():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT author FROM books ORDER BY author ASC')
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows if r[0]]

# Get books by category
def get_books_by_category(category):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, caption, author, category, tags, mime_type, file_id, file_path, date
        FROM books
        WHERE category = ?
        ORDER BY title ASC
    ''', (category,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "title": row[1],
            "caption": row[2],
            "author": row[3],
            "category": row[4],
            "tags": row[5],
            "mime_type": row[6],
            "file_id": row[7],
            "file_path": row[8],
            "date": row[9],
        } for row in rows
    ]

# Get books by author
def get_books_by_author(author):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, title, caption, author, category, tags, mime_type, file_id, file_path, date
        FROM books
        WHERE author = ?
        ORDER BY title ASC
    ''', (author,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "title": row[1],
            "caption": row[2],
            "author": row[3],
            "category": row[4],
            "tags": row[5],
            "mime_type": row[6],
            "file_id": row[7],
            "file_path": row[8],
            "date": row[9],
        } for row in rows
    ]

def book_exists(title, file_id=None):
    conn=sqlite3.connect(DB_PATH)
    cursor=conn.cursor()
    if file_id:
        cursor.execute("SELECT 1 FROM books  WHERE title=? OR file_id=?", (title,file_id))
    else: 
         cursor.execute("SELECT 1 FROM books WHERE title=?", (title,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists