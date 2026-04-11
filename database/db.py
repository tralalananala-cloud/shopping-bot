"""Inițializare bază de date PostgreSQL (Neon.tech via asyncpg)."""

import logging

from database.connection import get_pool

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """Creează tabelele dacă nu există."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id    BIGINT PRIMARY KEY,
                username   TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS personal_lists (
                id         BIGSERIAL PRIMARY KEY,
                user_id    BIGINT NOT NULL REFERENCES users(user_id),
                item       TEXT NOT NULL,
                quantity   TEXT DEFAULT '1',
                checked    INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id          BIGSERIAL PRIMARY KEY,
                name        TEXT NOT NULL,
                owner_id    BIGINT NOT NULL REFERENCES users(user_id),
                invite_code TEXT UNIQUE NOT NULL,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS group_members (
                group_id  BIGINT NOT NULL REFERENCES groups(id),
                user_id   BIGINT NOT NULL REFERENCES users(user_id),
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (group_id, user_id)
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS group_lists (
                id         BIGSERIAL PRIMARY KEY,
                group_id   BIGINT NOT NULL REFERENCES groups(id),
                item       TEXT NOT NULL,
                quantity   TEXT DEFAULT '1',
                checked    INTEGER DEFAULT 0,
                added_by   BIGINT NOT NULL REFERENCES users(user_id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    logger.info("Tabele PostgreSQL create/verificate cu succes.")
