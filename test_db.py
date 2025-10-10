# test_db.py

from database.models import create_tables
from database.db import insert_book, get_all_books

# 1. Create the table
#create_tables()

# 2. Insert a test record
insert_book(
title="Test Book",
caption="A sample book for testing.",
mime_type="application/pdf",
file_id="12345",
date="2025-10-09"
)

# 3. Retrieve and print records
books = get_all_books()
for book in books:
    print(book)
