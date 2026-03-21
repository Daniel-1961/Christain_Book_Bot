# database/remove_duplicates.py
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')

def remove_duplicates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find duplicates based on exact same title, author, and language
    # We will keep the one with the lowest ID (the first one added)
    
    query = """
    DELETE FROM books
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM books
        GROUP BY title, author, language
    )
    """
    
    # Let's see how many there are first
    cursor.execute("""
        SELECT title, author, COUNT(*) 
        FROM books 
        WHERE language = 'Amharic'
        GROUP BY title, author 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    duplicate_count = sum([count - 1 for _, _, count in duplicates])
    
    if duplicate_count > 0:
        print(f"Found {duplicate_count} duplicate Amharic books!")
        for title, author, count in duplicates:
            print(f" - {title} by {author} ({count} copies)")
            
        # Delete them
        cursor.execute(query)
        conn.commit()
        print(f"\n✅ Successfully deleted {duplicate_count} duplicate records.")
    else:
        print("No duplicates found based on exact Title + Author match.")
        
    conn.close()

if __name__ == "__main__":
    remove_duplicates()
