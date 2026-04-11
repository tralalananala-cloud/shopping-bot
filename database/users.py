"""CRUD pentru tabela users."""

import aiosqlite
from config import DB_PATH


async def ensure_user(user_id: int, username: str = None, first_name: str = None) -> None:
    """Înregistrează userul la prima interacțiune sau actualizează datele."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username   = COALESCE(excluded.username,   username),
                first_name = COALESCE(excluded.first_name, first_name)
            """,
            (user_id, username, first_name),
        )
        await db.commit()


async def get_user(user_id: int):
    """Returnează rândul userului sau None."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone()


async def get_display_name(user_id: int) -> str:
    """Returnează first_name sau username sau 'User #ID'."""
    user = await get_user(user_id)
    if user:
        return user["first_name"] or user["username"] or f"User #{user_id}"
    return f"User #{user_id}"
