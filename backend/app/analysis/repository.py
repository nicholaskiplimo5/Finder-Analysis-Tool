import asyncpg
import numpy as np


async def fetch_recent_digits(pool: asyncpg.Pool, symbol: str, limit: int) -> np.ndarray:
    """Last `limit` digits for `symbol`, in chronological (ascending
    epoch) order. The inner query does the epoch-ordered LIMIT (served by
    the (symbol, epoch) index) and only the resulting small window gets
    re-sorted ascending -- this never scans the full table."""
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT digit FROM (
                SELECT digit, epoch FROM ticks
                WHERE symbol = $1
                ORDER BY epoch DESC
                LIMIT $2
            ) recent
            ORDER BY epoch ASC
            """,
            symbol,
            limit,
        )
    return np.array([r["digit"] for r in rows], dtype=np.int64)
