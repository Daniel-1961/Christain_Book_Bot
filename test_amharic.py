import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from channel_scraper.amharic_scraper import extract_title_from_caption, extract_author_from_caption

# ========================================
# 3 Real captions from the user's channel
# ========================================

caption1 = """ይህን መጽሐፍ ለonly Jesusሶች በመስጠት ከምንፍቅና እንታደጋቸው።
ቀደም ሲል በሐዋሪያት ቤተክርስትያን ሲያስተምር የቆዩ ነበሩ።
📚ስም፦ ኢየሱስ ራሱ እግዚአብሔር አብና መንፈስ ቅዱስ ነውን?
👤ጸሐፊ፦ ፍሬው ቤዛ
፡
ይ🀄️ላ🀄️ሉን....."""

caption2 = """@amharicspritualbooks
ርዕስ፦  ዲያብሎስና እንቅስቃሴው
👤ጸሐፊ፦ ዶ/ር መለሰ ወጉ
👇👇👇👇👇👇👇
ሌሎች መንፈሳዊ መጽሐፍቶችና መንፈሳዊ መጽሔቶች እንዲደርሳችሁ ቻናላችንን ይቀላቀሉ።
@amharicspritualbooks"""

caption3 = """ሊነበብ የሚገባ መጽሐፍ!
📚ስም፦ ድል ነሺ ህይወት 
👤ጸሐፊ፦ ዎችማ ኒ 
🗣ተርጓሚ፦ ነብዩ ኢሳያስ"""

print("=" * 55)
print("  AMHARIC CAPTION EXTRACTION TEST")
print("=" * 55)

for i, (cap, label) in enumerate([
    (caption1, "📚ስም፦ pattern"),
    (caption2, "ርዕስ፦ pattern (no emoji)"),
    (caption3, "📚ስም፦ + 🗣ተርጓሚ pattern"),
], 1):
    title = extract_title_from_caption(cap, "fallback_file.pdf")
    author = extract_author_from_caption(cap)
    print(f"\n--- TEST {i}: {label} ---")
    print(f"  TITLE:  {title}")
    print(f"  AUTHOR: {author}")

print("\n" + "=" * 55)
print("  DONE")
print("=" * 55)
