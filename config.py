import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN nu este setat în fișierul .env!")

DB_PATH       = os.getenv("DB_PATH", "shopping.db")
DATA_JSON_PATH = "data.json"   # folosit doar la migrarea inițială
