"""CRUD pentru grupuri, membri și lista de grup."""

import random
import string

import aiosqlite

from config import DB_PATH


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _random_code(k: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))


async def _unique_code() -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        while True:
            code = _random_code()
            cur = await db.execute("SELECT 1 FROM groups WHERE invite_code=?", (code,))
            if not await cur.fetchone():
                return code


# ---------------------------------------------------------------------------
# Grupuri
# ---------------------------------------------------------------------------

async def create_group(name: str, owner_id: int) -> int:
    """Creează grup, adaugă ownerul ca prim membru. Returnează group_id."""
    code = await _unique_code()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO groups (name, owner_id, invite_code) VALUES (?,?,?)",
            (name.strip(), owner_id, code),
        )
        gid = cur.lastrowid
        await db.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES (?,?)",
            (gid, owner_id),
        )
        await db.commit()
        return gid


async def get_group(group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute("SELECT * FROM groups WHERE id=?", (group_id,))
        return await cur.fetchone()


async def get_group_by_code(code: str):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM groups WHERE invite_code=?", (code.strip().upper(),)
        )
        return await cur.fetchone()


async def get_user_groups(user_id: int) -> list:
    """Grupurile la care participă userul."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT g.* FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = ?
            ORDER BY g.created_at DESC
            """,
            (user_id,),
        )
        return await cur.fetchall()


async def rename_group(group_id: int, new_name: str) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE groups SET name=? WHERE id=?", (new_name.strip(), group_id)
        )
        await db.commit()


async def delete_group(group_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM group_lists   WHERE group_id=?", (group_id,))
        await db.execute("DELETE FROM group_members WHERE group_id=?", (group_id,))
        await db.execute("DELETE FROM groups         WHERE id=?",       (group_id,))
        await db.commit()


# ---------------------------------------------------------------------------
# Membri
# ---------------------------------------------------------------------------

async def is_member(group_id: int, user_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT 1 FROM group_members WHERE group_id=? AND user_id=?",
            (group_id, user_id),
        )
        return bool(await cur.fetchone())


async def add_member(group_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?,?)",
            (group_id, user_id),
        )
        await db.commit()


async def remove_member(group_id: int, user_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM group_members WHERE group_id=? AND user_id=?",
            (group_id, user_id),
        )
        await db.commit()


async def get_members(group_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT u.user_id, u.username, u.first_name, gm.joined_at
            FROM group_members gm
            JOIN users u ON u.user_id = gm.user_id
            WHERE gm.group_id = ?
            ORDER BY gm.joined_at ASC
            """,
            (group_id,),
        )
        return await cur.fetchall()


async def member_count(group_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "SELECT COUNT(*) FROM group_members WHERE group_id=?", (group_id,)
        )
        return (await cur.fetchone())[0]


# ---------------------------------------------------------------------------
# Lista grupului
# ---------------------------------------------------------------------------

async def add_group_item(group_id: int, item: str, quantity: str, added_by: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "INSERT INTO group_lists (group_id, item, quantity, added_by) VALUES (?,?,?,?)",
            (group_id, item.strip(), quantity, added_by),
        )
        await db.commit()
        return cur.lastrowid


async def get_group_items(group_id: int) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            """
            SELECT gl.*, u.first_name, u.username
            FROM group_lists gl
            JOIN users u ON u.user_id = gl.added_by
            WHERE gl.group_id = ?
            ORDER BY gl.checked ASC, gl.id ASC
            """,
            (group_id,),
        )
        return await cur.fetchall()


async def get_group_item(item_id: int, group_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM group_lists WHERE id=? AND group_id=?",
            (item_id, group_id),
        )
        return await cur.fetchone()


async def toggle_group_item(item_id: int, group_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT checked FROM group_lists WHERE id=? AND group_id=?",
            (item_id, group_id),
        )
        row = await cur.fetchone()
        if not row:
            return False
        new_state = 0 if row["checked"] else 1
        await db.execute(
            "UPDATE group_lists SET checked=? WHERE id=? AND group_id=?",
            (new_state, item_id, group_id),
        )
        await db.commit()
        return bool(new_state)


async def delete_group_item(item_id: int, group_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute(
            "DELETE FROM group_lists WHERE id=? AND group_id=?",
            (item_id, group_id),
        )
        await db.commit()
        return cur.rowcount > 0


async def copy_personal_to_group(user_id: int, group_id: int, items: list) -> int:
    """Copiază itemii din lista personală în lista grupului. Returnează numărul copiat."""
    async with aiosqlite.connect(DB_PATH) as db:
        count = 0
        for item in items:
            await db.execute(
                "INSERT INTO group_lists (group_id, item, quantity, added_by) VALUES (?,?,?,?)",
                (group_id, item["item"], item["quantity"], user_id),
            )
            count += 1
        await db.commit()
        return count
