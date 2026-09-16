"""Historical backfill via ticks_history, used for:

- cold start (empty table): seed up to `max_count` recent ticks
- reconnect / downtime: fill from the last stored epoch to now
- in-stream gap healing: fill a narrow range noticed on the live path

All three share the same paginated fetch + idempotent insert. Inserts use
ON CONFLICT DO NOTHING (see db.insert_ticks), so overlapping ranges from
concurrent callers are safe -- order of arrival doesn't matter.
"""

from collections.abc import AsyncIterator
from decimal import Decimal

import asyncpg

from app.db import insert_ticks
from app.ingestion.deriv_ws import DerivConnection
from app.ingestion.digits import extract_digit
from app.models import SymbolMeta, Tick

RawPoint = tuple[int, Decimal]


async def _paginated_history(
    conn: DerivConnection,
    symbol: str,
    *,
    start_epoch: int | None,
    page_size: int,
    max_count: int | None,
) -> AsyncIterator[list[RawPoint]]:
    """Yield pages of (epoch, quote) walking backward from latest until
    `start_epoch` is reached (exclusive) or `max_count` points fetched."""
    cursor_end: int | str = "latest"
    fetched = 0

    while True:
        remaining = None if max_count is None else max_count - fetched
        if remaining is not None and remaining <= 0:
            return
        count = page_size if remaining is None else min(page_size, remaining)

        response = await conn.send_request(
            {
                "ticks_history": symbol,
                "count": count,
                "end": cursor_end,
                "style": "ticks",
            }
        )
        history = response.get("history")
        if not history or not history.get("times"):
            return

        times: list[int] = history["times"]
        prices: list[Decimal] = [
            p if isinstance(p, Decimal) else Decimal(str(p)) for p in history["prices"]
        ]
        page = list(zip(times, prices))

        if start_epoch is not None:
            page = [(e, q) for e, q in page if e > start_epoch]

        if page:
            fetched += len(page)
            yield page

        oldest_in_response = times[0]
        if start_epoch is not None and oldest_in_response <= start_epoch:
            return
        if len(times) < count:
            return  # exhausted available history before reaching the target
        cursor_end = oldest_in_response - 1


def _make_tick(meta: SymbolMeta, epoch: int, quote: Decimal) -> Tick:
    return Tick(
        symbol=meta.symbol,
        epoch=epoch,
        quote=quote,
        digit=extract_digit(quote, meta.decimals),
    )


async def backfill_range(
    conn: DerivConnection,
    pool: asyncpg.Pool,
    meta: SymbolMeta,
    *,
    start_epoch: int | None,
    page_size: int,
    max_count: int | None = None,
) -> int:
    """Backfill (start_epoch, now] for one symbol. Returns ticks written.

    `start_epoch=None` means cold start: pull up to `max_count` most
    recent ticks with no lower bound other than that budget.
    """
    total = 0
    async for page in _paginated_history(
        conn,
        meta.symbol,
        start_epoch=start_epoch,
        page_size=page_size,
        max_count=max_count,
    ):
        ticks = [_make_tick(meta, epoch, quote) for epoch, quote in page]
        await insert_ticks(pool, ticks)
        total += len(ticks)
    return total
