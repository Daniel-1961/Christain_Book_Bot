# database/fix_unknown_authors.py
"""
Script to update existing Amharic books in the database that have
'Unknown' as the author or 'Other' as the category, using the
improved regex logic from the Amharic scraper.
"""
import sys
import os
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from channel_scraper.amharic_scraper import extract_author_from_caption, detect_amharic_category, extract_title_from_caption

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'data', 'books.db')

def fix_records():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all Amharic books that have Unknown author
    cursor.execute("SELECT id, title, caption, category, author, file_path FROM books WHERE language = 'Amharic'")
    books = cursor.fetchall()
    
    updated_count = 0
    
    for book_id, title, caption, category, author, file_path in books:
        if not caption:
            continue
            
        new_author = extract_author_from_caption(caption)
        new_title = extract_title_from_caption(caption, title)
        new_category = detect_amharic_category(f"{new_title} {caption}")
        
        needs_update = False
        
        # Check if we improved the author
        if new_author != "Unknown" and author != new_author:
            needs_update = True
            
        # Check if we improved the category
        if new_category != "Other" and category != new_category:
            needs_update = True
            
        if needs_update:
            cursor.execute('''
                UPDATE books 
                SET title = ?, author = ?, category = ? 
                WHERE id = ?
            ''', (new_title, new_author, new_category, book_id))
            updated_count += 1
            print(f"✅ Fixed Book ID {book_id}:")
            print(f"   Old -> {author} | {category}")
            print(f"   New -> {new_author} | {new_category}")
            
    conn.commit()
    conn.close()
    
    print(f"\n🎯 Successfully updated {updated_count} books in the database.")

if __name__ == "__main__":
    fix_records()
