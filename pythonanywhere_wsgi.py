"""PythonAnywhere WSGI configuration file.

Copy this into /var/www/danu1961_pythonanywhere_com_wsgi.py
on PythonAnywhere (Web tab → click the WSGI file link).
"""
import sys
import os

# ----- Project path -----
project_home = '/home/Danu1961/Christian_Book_Bot'
if project_home not in sys.path:
    sys.path.insert(0, project_home)
os.chdir(project_home)

# ----- Virtualenv -----
activate_this = '/home/Danu1961/.virtualenvs/botenv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

# ----- Environment variables (set here since free tier has no env panel) -----
os.environ['BOT_TOKEN'] = '8230963372:AAFnQZjOx8JW7qV-Q7NycoMGP2chcwukhlE'
os.environ['ARCHIVE_CHAT_ID'] = '-1002872260893'

# ----- Import Flask app -----
from bot.webhook_app import app as application
