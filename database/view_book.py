import os
import sqlite3

def view_books():
    base_dir = os.path.dirname(os.path.dirname(__file__))  # Go up to project root
    db_path = os.path.join(base_dir, 'data', 'books.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT id, title, caption, mime_type, date FROM books')
    rows = cursor.fetchall()

    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Title: {row[1]}")
        print(f"Caption: {row[2]}")
        print(f"Type: {row[3]}")
        print(f"Date: {row[4]}")
        print("-" * 40)

    conn.close()

view_books()