"""CRUD pentru tabela users (asyncpg / PostgreSQL)."""

from database.connection import get_pool


async def ensure_user(user_id: int, username: str = None, first_name: str = None) -> None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO users (user_id, username, first_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE SET
                username   = COALESCE(EXCLUDED.username,   users.username),
                first_name = COALESCE(EXCLUDED.first_name, users.first_name)
        """, user_id, username, first_name)


async def get_user(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )


async def get_display_name(user_id: int) -> str:
    user = await get_user(user_id)
    if user:
        return user["first_name"] or user["username"] or f"User #{user_id}"
    return f"User #{user_id}"
