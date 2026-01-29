"""Helper WSGI file for PythonAnywhere.

Copy this file's contents into your PythonAnywhere WSGI file (the one
under /var/www/youraccount_pythonanywhere_com_wsgi.py) or point PA at
this file. It will try several candidate paths and fall back to
scanning your home directory for a folder that contains `bot/`.

Edit the `candidates` list if you know your exact project path. Do NOT
hardcode secrets here; set `BOT_TOKEN` in the PythonAnywhere Web ->
Environment variables panel instead.
"""
import sys
import os

# Try a few likely names first (edit these to match your project)
candidates = [
    '/home/Danu1961/Christian_Book_Bot',
    '/home/Danu1961/Christain_Book_Bot',
    '/home/Danu1961/christian_books_bot',
    '/home/Danu1961/Christian-Book-Bot',
    '/home/Danu1961/christian-books-bot',
]

project_home = None
for p in candidates:
    if os.path.isdir(p):
        project_home = p
        break

# Fallback: scan home directory for a folder that contains `bot/`
if project_home is None:
    home = os.path.expanduser('~')
    for entry in os.listdir(home):
        p = os.path.join(home, entry)
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, 'bot')):
            project_home = p
            break

if project_home is None:
    raise FileNotFoundError("Project directory containing 'bot/' not found.\n"
                            "Edit the WSGI file to set the correct path.")

# Ensure project is on sys.path
if project_home not in sys.path:
    sys.path.insert(0, project_home)

try:
    os.chdir(project_home)
except Exception:
    pass

# If you use a virtualenv on PythonAnywhere, activate it here by
# uncommenting and editing the path below:
# activate_this = '/home/Danu1961/.virtualenvs/yourenv/bin/activate_this.py'
# with open(activate_this) as f:
#     exec(f.read(), dict(__file__=activate_this))

# Ensure BOT_TOKEN is set in the environment (recommended to set via
# PythonAnywhere Web -> Environment variables). Uncomment to set
# a fallback token (NOT recommended for production):
# os.environ.setdefault('BOT_TOKEN', 'PUT_YOUR_TOKEN_HERE')

# Finally import the Flask app and expose it as `application` for WSGI.
from bot.webhook_app import app as application
