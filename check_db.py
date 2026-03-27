import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "books.db")
print(f"Database path: {db_path}")
print(f"File exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    size_kb = os.path.getsize(db_path) / 1024
    print(f"File size: {size_kb:.1f} KB")
    
    db = sqlite3.connect(db_path)
    c = db.cursor()
    
    total = c.execute("SELECT COUNT(1) FROM books").fetchone()[0]
    print(f"\nTotal books: {total}")
    
    # Check by language
    langs = c.execute("SELECT language, COUNT(1) FROM books GROUP BY language").fetchall()
    for lang, count in langs:
        print(f"  {lang or 'No Language'}: {count}")
    
    # Show a few Amharic samples
    amharic = c.execute("SELECT title, author FROM books WHERE language='Amharic' LIMIT 5").fetchall()
    if amharic:
        print(f"\nSample Amharic books:")
        for t, a in amharic:
            print(f"  - {t} (by {a})")
    else:
        print("\n*** NO AMHARIC BOOKS FOUND! They were likely wiped by git pull. ***")
    
    db.close()
else:
    print("*** DATABASE FILE NOT FOUND! ***")
