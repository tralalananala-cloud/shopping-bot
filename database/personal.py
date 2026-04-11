"""CRUD pentru lista personală a unui user."""

import aiosqlite
from config import DB_PATH


async def add_item(user_id: int, item: str, quantity: str = "1") -> int:
    """Adaugă produs și returnează id-ul."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO personal_lists (user_id, item, quantity) VALUES (?,?,?)",
            (user_id, item.strip(), quantity),
        )
        await db.commit()
        return cur.lastrowid


async def get_items(user_id: int) -> list:
    """Returnează toate produsele userului, necumpărate primele."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM personal_lists WHERE user_id=? ORDER BY checked ASC, id ASC",
            (user_id,),
        )
        return await cursor.fetchall()


async def get_item(item_id: int, user_id: int):
    """Returnează un produs (verificând că aparține userului)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM personal_lists WHERE id=? AND user_id=?",
            (item_id, user_id),
        )
        return await cur.fetchone()


async def toggle_item(item_id: int, user_id: int) -> bool:
    """Comută starea checked. Returnează noua stare."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT checked FROM personal_lists WHERE id=? AND user_id=?",
            (item_id, user_id),
        )
        row = await cur.fetchone()
        if not row:
            return False
        new_state = 0 if row["checked"] else 1
        await db.execute(
            "UPDATE personal_lists SET checked=? WHERE id=? AND user_id=?",
            (new_state, item_id, user_id),
        )
        await db.commit()
        return bool(new_state)


async def delete_item(item_id: int, user_id: int) -> bool:
    """Șterge produs. Returnează True dacă a existat."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM personal_lists WHERE id=? AND user_id=?",
            (item_id, user_id),
        )
        await db.commit()
        return cur.rowcount > 0


async def clear_checked(user_id: int) -> int:
    """Șterge toate produsele bifate. Returnează numărul șters."""
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM personal_lists WHERE user_id=? AND checked=1",
            (user_id,),
        )
        await db.commit()
        return cur.rowcount
