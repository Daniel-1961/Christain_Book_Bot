import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from channel_scraper.amharic_scraper import (
    extract_title_from_caption,
    extract_author_from_caption,
    is_english_book,
)

# ============================================
# TEST 1: Caption with ፦ separator
# ============================================
caption1 = """📔ርዕስ፦የዓለማችን ሁኔታዎችና የመጽሐፍ ቅዱስ ትንቢቶች
👤ደራሲ፦ቻርለስ ዳየር(ዶ/ር)
🗣ተርጓሚ፦አሸብር ከተማ(መጋቢ)
💾መጠን፦5.9MB 📑የገጽ ብዛት፦231"""

# ============================================
# TEST 2: Caption with :- separator
# ============================================
caption2 = """📔ርዕስ:-መስቀሉን ማኮሰስ ፣ ስቅሉን ማራከስ
👤ጸሐፊ:-ጳውሎስ ፈቃዱ
💾መጠን፦0.89MB 📑የገጽ ብዛት፦15"""

# ============================================
# TEST 3: Caption with ፦ separator (different author)
# ============================================
caption3 = """📔ርዕስ፦ወቅታዊ ዘላለማዊ
👤ጸሐፊ፦ንጉሴ ቡልቻ(ጋሽ)
📑የገጽ ብዛት፦144 💾መጠን:-2.4MB"""

# ============================================
# TEST 4: English book (SHOULD BE SKIPPED)
# ============================================
caption_eng = """Book፦Surprised by Joy: The Shape of My Early Life
👤Author፦C. S. Lewis(1955)
📑Page፦167 💾Size፦1.0"""

print("=" * 50)
print("  AMHARIC SCRAPER REGEX TEST RESULTS")
print("=" * 50)

for i, (cap, label) in enumerate([
    (caption1, "Caption 1 (፦ separator)"),
    (caption2, "Caption 2 (:- separator)"),
    (caption3, "Caption 3 (፦ different author)"),
], 1):
    title = extract_title_from_caption(cap, "fallback.pdf")
    author = extract_author_from_caption(cap)
    eng = is_english_book(cap)
    print(f"\n--- TEST {i}: {label} ---")
    print(f"  TITLE:   {title}")
    print(f"  AUTHOR:  {author}")
    print(f"  English? {eng}")

print(f"\n--- TEST 4: English book (should be SKIPPED) ---")
title_e = extract_title_from_caption(caption_eng, "fallback.pdf")
author_e = extract_author_from_caption(caption_eng)
eng_e = is_english_book(caption_eng)
print(f"  TITLE:   {title_e}")
print(f"  AUTHOR:  {author_e}")
print(f"  English? {eng_e}  <-- Must be True to skip!")

print("\n" + "=" * 50)
print("  TEST COMPLETE")
print("=" * 50)
