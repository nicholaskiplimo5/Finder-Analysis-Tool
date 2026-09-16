from collections.abc import Iterable

import asyncpg

from app.models import SymbolMeta, Tick


async def create_pool(dsn: str) -> asyncpg.Pool:
    return await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=10)


async def upsert_symbol_meta(pool: asyncpg.Pool, metas: Iterable[SymbolMeta]) -> None:
    rows = [(m.symbol, m.pip_size, m.decimals) for m in metas]
    if not rows:
        return
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO symbol_meta (symbol, pip_size, decimals, updated_at)
            VALUES ($1, $2, $3, now())
            ON CONFLICT (symbol) DO UPDATE
                SET pip_size = EXCLUDED.pip_size,
                    decimals = EXCLUDED.decimals,
                    updated_at = now()
            """,
            rows,
        )


async def get_last_epoch(pool: asyncpg.Pool, symbol: str) -> int | None:
    async with pool.acquire() as conn:
        return await conn.fetchval(
            "SELECT max(epoch) FROM ticks WHERE symbol = $1", symbol
        )


async def insert_ticks(pool: asyncpg.Pool, ticks: list[Tick]) -> None:
    if not ticks:
        return
    rows = [(t.symbol, t.epoch, t.quote, t.digit) for t in ticks]
    async with pool.acquire() as conn:
        await conn.executemany(
            """
            INSERT INTO ticks (symbol, epoch, quote, digit)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (symbol, epoch) DO NOTHING
            """,
            rows,
        )
