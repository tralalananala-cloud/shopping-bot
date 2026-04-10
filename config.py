import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN nu este setat! Copiază .env.example în .env și completează tokenul.")

# Categorii predefinite cu emoji
CATEGORIES = {
    "lactate": "🥛 Lactate",
    "carne": "🥩 Carne",
    "legume": "🥦 Legume",
    "fructe": "🍎 Fructe",
    "igiena": "🧴 Igienă",
    "panificatie": "🍞 Panificație",
    "altele": "🛒 Altele",
}

DEFAULT_CATEGORY = "altele"
DATA_FILE = "data.json"
MAX_HISTORY = 20  # numărul maxim de acțiuni reținute pentru undo
