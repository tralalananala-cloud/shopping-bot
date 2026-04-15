"""CRUD pentru lista personală (asyncpg / PostgreSQL)."""

from database.connection import get_pool


async def add_item(user_id: int, item: str, quantity: str = "1", priority: int = 2) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO personal_lists (user_id, item, quantity, priority) VALUES ($1, $2, $3, $4) RETURNING id",
            user_id, item.strip(), quantity, priority,
        )
        return row["id"]


async def get_items(user_id: int) -> list:
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetch(
            "SELECT * FROM personal_lists WHERE user_id=$1 ORDER BY checked ASC, priority DESC, id DESC",
            user_id,
        )


async def get_item(item_id: int, user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM personal_lists WHERE id=$1 AND user_id=$2",
            item_id, user_id,
        )


async def toggle_item(item_id: int, user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT checked FROM personal_lists WHERE id=$1 AND user_id=$2",
            item_id, user_id,
        )
        if not row:
            return False
        new_state = 0 if row["checked"] else 1
        await conn.execute(
            "UPDATE personal_lists SET checked=$1 WHERE id=$2 AND user_id=$3",
            new_state, item_id, user_id,
        )
        return bool(new_state)


async def delete_item(item_id: int, user_id: int) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM personal_lists WHERE id=$1 AND user_id=$2",
            item_id, user_id,
        )
        return result != "DELETE 0"


async def clear_checked(user_id: int) -> int:
    pool = await get_pool()
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM personal_lists WHERE user_id=$1 AND checked=1",
            user_id,
        )
        return int(result.split()[-1])
