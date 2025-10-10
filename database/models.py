# database/models.py
import sqlite3
import os

def create_tables():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Project root
    db_path = os.path.join(base_dir, 'data', 'books.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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
            date TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("✅ Database initialized with file_path column")
