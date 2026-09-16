import asyncio
import json
from collections.abc import AsyncIterator

import asyncpg
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_pool, get_settings, valid_symbol
from app.config import Settings
from app.db import fetch_ticks_since, get_last_epoch

router = APIRouter(prefix="/api", tags=["live"])


async def _event_stream(
    request: Request, pool: asyncpg.Pool, symbol: str, poll_interval: float
) -> AsyncIterator[str]:
    # Start from whatever the latest stored epoch is *right now* -- a
    # client that just connected gets only new ticks going forward, not
    # a replay of the symbol's whole history.
    last_epoch = await get_last_epoch(pool, symbol)
    if last_epoch is None:
        last_epoch = -1

    while True:
        if await request.is_disconnected():
            return
        await asyncio.sleep(poll_interval)

        new_ticks = await fetch_ticks_since(pool, symbol, last_epoch)
        for tick in new_ticks:
            last_epoch = tick.epoch
            payload = {
                "symbol": tick.symbol,
                "epoch": tick.epoch,
                "quote": str(tick.quote),
                "digit": tick.digit,
            }
            yield f"data: {json.dumps(payload)}\n\n"


@router.get("/live-ticks/{symbol}")
async def live_ticks(
    request: Request,
    symbol: str = Depends(valid_symbol),
    pool: asyncpg.Pool = Depends(get_pool),
    settings: Settings = Depends(get_settings),
) -> StreamingResponse:
    return StreamingResponse(
        _event_stream(request, pool, symbol, settings.live_tick_poll_interval_seconds),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
