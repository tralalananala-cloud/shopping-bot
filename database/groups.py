"""CRUD pentru grupuri, membri și lista de grup (asyncpg / PostgreSQL)."""

import random
import string

from database.connection import get_pool


def _random_code(k: int = 6) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))


async def _unique_code() -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        while True:
            code = _random_code()
            row = await conn.fetchrow("SELECT 1 FROM groups WHERE invite_code=$1", code)
            if not row:
                return code


# ---------------------------------------------------------------------------
# Grupuri
# ---------------------------------------------------------------------------

async def create_group(name: str, owner_id: int) -> int:
    code = await _unique_code()
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO groups (name, owner_id, invite_code) VALUES ($1, $2, $3) RETURNING id",
            name.strip(), owner_id, code,
        )
        gid = row["id"]
        await conn.execute(
            "INSERT INTO group_members (group_id, user_id) VALUES ($1, $2)",
            gid, owner_id,
        )
        return gid


async def get_group(group_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow("SELECT * FROM groups WHERE id=$1", group_id)


async def get_group_by_code(code: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM groups WHERE invite_code=$1", code.strip().upper()
        )


async def get_user_groups(user_id: int) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT g.* FROM groups g
            JOIN group_members gm ON g.id = gm.group_id
            WHERE gm.user_id = $1
            ORDER BY g.created_at DESC
        """, user_id)


async def rename_group(group_id: int, new_name: str) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE groups SET name=$1 WHERE id=$2", new_name.strip(), group_id
        )


async def delete_group(group_id: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("DELETE FROM group_lists   WHERE group_id=$1", group_id)
        await conn.execute("DELETE FROM group_members WHERE group_id=$1", group_id)
        await conn.execute("DELETE FROM groups        WHERE id=$1",       group_id)


# ---------------------------------------------------------------------------
# Membri
# ---------------------------------------------------------------------------

async def is_member(group_id: int, user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT 1 FROM group_members WHERE group_id=$1 AND user_id=$2",
            group_id, user_id,
        )
        return bool(row)


async def add_member(group_id: int, user_id: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO group_members (group_id, user_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
        """, group_id, user_id)


async def remove_member(group_id: int, user_id: int) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "DELETE FROM group_members WHERE group_id=$1 AND user_id=$2",
            group_id, user_id,
        )


async def get_members(group_id: int) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT u.user_id, u.username, u.first_name, gm.joined_at
            FROM group_members gm
            JOIN users u ON u.user_id = gm.user_id
            WHERE gm.group_id = $1
            ORDER BY gm.joined_at ASC
        """, group_id)


async def get_member_ids(group_id: int) -> list[int]:
    """Returnează lista de user_id ale tuturor membrilor grupului."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT user_id FROM group_members WHERE group_id=$1", group_id
        )
        return [r["user_id"] for r in rows]


async def member_count(group_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT COUNT(*) AS cnt FROM group_members WHERE group_id=$1", group_id
        )
        return row["cnt"]


# ---------------------------------------------------------------------------
# Lista grupului
# ---------------------------------------------------------------------------

async def add_group_item(group_id: int, item: str, quantity: str, added_by: int, priority: int = 2) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO group_lists (group_id, item, quantity, added_by, priority) VALUES ($1,$2,$3,$4,$5) RETURNING id",
            group_id, item.strip(), quantity, added_by, priority,
        )
        return row["id"]


async def get_group_items(group_id: int) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT gl.*, u.first_name, u.username
            FROM group_lists gl
            JOIN users u ON u.user_id = gl.added_by
            WHERE gl.group_id = $1
            ORDER BY gl.checked ASC, gl.priority DESC, gl.id DESC
        """, group_id)


async def get_group_item(item_id: int, group_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM group_lists WHERE id=$1 AND group_id=$2",
            item_id, group_id,
        )


async def toggle_group_item(item_id: int, group_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT checked FROM group_lists WHERE id=$1 AND group_id=$2",
            item_id, group_id,
        )
        if not row:
            return False
        new_state = 0 if row["checked"] else 1
        await conn.execute(
            "UPDATE group_lists SET checked=$1 WHERE id=$2 AND group_id=$3",
            new_state, item_id, group_id,
        )
        return bool(new_state)


async def delete_group_item(item_id: int, group_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM group_lists WHERE id=$1 AND group_id=$2",
            item_id, group_id,
        )
        return result != "DELETE 0"


async def clear_group_checked(group_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM group_lists WHERE group_id=$1 AND checked=1",
            group_id,
        )
        return int(result.split()[-1])


async def copy_personal_to_group(user_id: int, group_id: int, items: list) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        count = 0
        for item in items:
            await conn.execute(
                "INSERT INTO group_lists (group_id, item, quantity, added_by) VALUES ($1,$2,$3,$4)",
                group_id, item["item"], item["quantity"], user_id,
            )
            count += 1
        return count


async def get_feed(user_id: int) -> list:
    """Returnează toate produsele (personal + grupuri) pentru feed."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch("""
            SELECT
                'personal'::TEXT AS source,
                NULL::BIGINT      AS group_id,
                NULL::TEXT        AS group_name,
                COALESCE(u.first_name, u.username, 'Tu') AS added_by_name,
                pl.id, pl.item, pl.quantity, pl.priority, pl.checked, pl.created_at
            FROM personal_lists pl
            JOIN users u ON u.user_id = pl.user_id
            WHERE pl.user_id = $1

            UNION ALL

            SELECT
                'group'::TEXT AS source,
                g.id          AS group_id,
                g.name        AS group_name,
                COALESCE(u.first_name, u.username, 'Utilizator') AS added_by_name,
                gl.id, gl.item, gl.quantity, gl.priority, gl.checked, gl.created_at
            FROM group_lists gl
            JOIN groups g ON g.id = gl.group_id
            JOIN group_members gm ON gm.group_id = g.id AND gm.user_id = $1
            JOIN users u ON u.user_id = gl.added_by

            ORDER BY checked ASC, priority DESC, created_at DESC
            LIMIT 200
        """, user_id)
