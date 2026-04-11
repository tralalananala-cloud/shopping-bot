"""
Inițializare bază de date SQLite și migrare din formatul vechi JSON.
"""

import json
import logging
import os
import random
import string

import aiosqlite

from config import DATA_JSON_PATH, DB_PATH

logger = logging.getLogger(__name__)


async def get_db() -> aiosqlite.Connection:
    """Returnează o conexiune async la DB cu row_factory setat."""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    """Creează tabelele dacă nu există, apoi migrează datele vechi."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    INTEGER PRIMARY KEY,
                username   TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS personal_lists (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id    INTEGER NOT NULL,
                item       TEXT    NOT NULL,
                quantity   TEXT    DEFAULT '1',
                checked    INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS groups (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                owner_id    INTEGER NOT NULL,
                invite_code TEXT    UNIQUE NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS group_members (
                group_id  INTEGER NOT NULL,
                user_id   INTEGER NOT NULL,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id),
                FOREIGN KEY (group_id) REFERENCES groups(id),
                FOREIGN KEY (user_id)  REFERENCES users(user_id)
            );

            CREATE TABLE IF NOT EXISTS group_lists (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id   INTEGER NOT NULL,
                item       TEXT    NOT NULL,
                quantity   TEXT    DEFAULT '1',
                checked    INTEGER DEFAULT 0,
                added_by   INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (group_id) REFERENCES groups(id),
                FOREIGN KEY (added_by) REFERENCES users(user_id)
            );
        """)
        await db.commit()

    await _migrate_from_json()


# ---------------------------------------------------------------------------
# Migrare date din data.json (format vechi)
# ---------------------------------------------------------------------------

def _random_code(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def _migrate_from_json() -> None:
    """Migrează datele din data.json (dacă există și DB-ul e gol)."""
    if not os.path.exists(DATA_JSON_PATH):
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        if (await cursor.fetchone())[0] > 0:
            return  # deja migrat

    try:
        with open(DATA_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "users" not in data or "groups" not in data:
            return

        users_map  = data["users"]   # {user_id_str: group_id_str}
        groups_map = data["groups"]  # {group_id_str: {...}}

        async with aiosqlite.connect(DB_PATH) as db:
            # 1. Creăm toți userii
            for uid_str in users_map:
                await db.execute(
                    "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?,?,?)",
                    (int(uid_str), f"user_{uid_str}", f"User {uid_str[-4:]}"),
                )

            # 2. Procesăm fiecare grup o singură dată
            processed = set()
            for uid_str, gid_str in users_map.items():
                if gid_str in processed:
                    continue
                processed.add(gid_str)

                group   = groups_map.get(gid_str, {})
                members = group.get("members", [int(uid_str)])
                items   = group.get("items",   [])
                owner   = group.get("owner",   int(uid_str))

                if len(members) <= 1:
                    # Grup personal → migrăm în personal_lists
                    for item in items:
                        await db.execute(
                            "INSERT INTO personal_lists (user_id, item, quantity, checked) VALUES (?,?,?,?)",
                            (int(uid_str), item["name"], "1", 1 if item.get("done") else 0),
                        )
                else:
                    # Grup partajat → migrăm în groups + group_lists
                    code = group.get("invite_code") or _random_code()
                    cur  = await db.execute(
                        "INSERT INTO groups (name, owner_id, invite_code) VALUES (?,?,?)",
                        ("Listă partajată", owner, code),
                    )
                    new_gid = cur.lastrowid
                    for mid in members:
                        if isinstance(mid, int):
                            await db.execute(
                                "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?,?)",
                                (new_gid, mid),
                            )
                    for item in items:
                        await db.execute(
                            "INSERT INTO group_lists (group_id, item, quantity, checked, added_by) VALUES (?,?,?,?,?)",
                            (new_gid, item["name"], "1", 1 if item.get("done") else 0, owner),
                        )

            await db.commit()
        logger.info("Migrare din data.json completă.")

    except Exception as exc:
        logger.error("Eroare la migrare: %s", exc)
