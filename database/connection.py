"""Pool de conexiuni asyncpg pentru PostgreSQL (Neon.tech)."""

import logging
import os

import asyncpg

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        url = os.environ.get("DATABASE_URL", "")
        if not url:
            raise RuntimeError("DATABASE_URL nu este setat!")
        # Neon returnează uneori 'postgres://' — asyncpg vrea 'postgresql://'
        url = url.replace("postgres://", "postgresql://", 1)
        _pool = await asyncpg.create_pool(url, min_size=1, max_size=5)
        logger.info("Pool PostgreSQL inițializat.")
    return _pool
