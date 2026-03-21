# database/models.py
import sqlite3
import os


def create_tables():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Project root
    db_path = os.path.join(base_dir, 'data', 'books.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            caption TEXT,
            author TEXT,
            category TEXT,
            tags TEXT,
            mime_type TEXT,
            file_id TEXT,
            file_path TEXT,
            date TEXT,
            language TEXT DEFAULT 'English'
        )
    ''')

    # Users table (for tracking monthly active users)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()


def migrate_add_language_column():
    """Add language column to existing books table if it doesn't exist."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'data', 'books.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if column exists
    cursor.execute("PRAGMA table_info(books)")
    columns = [col[1] for col in cursor.fetchall()]

    if "language" not in columns:
        cursor.execute("ALTER TABLE books ADD COLUMN language TEXT DEFAULT 'English'")
        print("✅ Added 'language' column to books table")
    else:
        print("ℹ️ 'language' column already exists")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_tables()
    migrate_add_language_column()
    print("✅ Database initialized with users table and language support")
