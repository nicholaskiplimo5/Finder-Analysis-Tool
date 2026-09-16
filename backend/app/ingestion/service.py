import asyncio
import logging
from decimal import Decimal

import asyncpg

from app.config import Settings
from app.db import create_pool, get_last_epoch, insert_ticks, upsert_symbol_meta
from app.ingestion.backfill import backfill_range
from app.ingestion.deriv_ws import DerivConnection
from app.ingestion.digits import expected_interval_seconds, extract_digit
from app.ingestion.symbols import fetch_symbol_meta
from app.ingestion.watchdog import StalenessWatchdog, make_threshold_fn
from app.models import SymbolMeta, Tick

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool: asyncpg.Pool | None = None
        self._conn: DerivConnection | None = None

        self._meta: dict[str, SymbolMeta] = {}
        self._last_epoch: dict[str, int] = {}
        self._write_queue: asyncio.Queue[Tick] = asyncio.Queue()

        self._watchdog = StalenessWatchdog(
            settings.symbols,
            threshold_seconds=make_threshold_fn(
                expected_interval_seconds,
                multiplier=settings.staleness_multiplier,
                floor_seconds=settings.staleness_floor_seconds,
            ),
            on_stale=self._on_stale,
            check_interval_seconds=settings.watchdog_check_interval_seconds,
        )

    async def run(self) -> None:
        self._pool = await create_pool(self._settings.database_url)
        self._conn = DerivConnection(
            self._settings.deriv_ws_url,
            ping_interval_seconds=self._settings.ping_interval_seconds,
            request_timeout_seconds=self._settings.request_timeout_seconds,
            reconnect_backoff_base_seconds=self._settings.reconnect_backoff_base_seconds,
            reconnect_backoff_max_seconds=self._settings.reconnect_backoff_max_seconds,
            on_reconnect=self._on_reconnect,
        )

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._conn.run())
            tg.create_task(self._watchdog.run())
            tg.create_task(self._writer_loop())

    async def _on_reconnect(self) -> None:
        """Runs on first connect and every reconnect: (re)establish symbol
        metadata once, then bring every symbol's data up to date and
        (re)subscribe to live ticks, per symbol, independently."""
        assert self._conn is not None and self._pool is not None

        if not self._meta:
            self._meta = await fetch_symbol_meta(self._conn, self._settings.symbols)
            await upsert_symbol_meta(self._pool, self._meta.values())

        await asyncio.gather(
            *(self._sync_symbol(symbol) for symbol in self._settings.symbols)
        )

    async def _sync_symbol(self, symbol: str) -> None:
        assert self._conn is not None and self._pool is not None
        meta = self._meta[symbol]

        last_epoch = await get_last_epoch(self._pool, symbol)
        if last_epoch is None:
            written = await backfill_range(
                self._conn,
                self._pool,
                meta,
                start_epoch=None,
                page_size=self._settings.history_page_size,
                max_count=self._settings.cold_start_backfill_count,
            )
            logger.info("cold-start backfill for %s: %d ticks", symbol, written)
        else:
            written = await backfill_range(
                self._conn,
                self._pool,
                meta,
                start_epoch=last_epoch,
                page_size=self._settings.history_page_size,
            )
            if written:
                logger.info("gap backfill for %s: %d ticks", symbol, written)

        current_last = await get_last_epoch(self._pool, symbol)
        self._last_epoch[symbol] = current_last or 0

        await self._conn.subscribe_ticks(symbol, self._make_tick_handler(symbol))
        self._watchdog.mark(symbol)

    def _make_tick_handler(self, symbol: str):
        meta = self._meta[symbol]
        interval = expected_interval_seconds(symbol)
        gap_threshold = interval * self._settings.gap_multiplier

        async def handle(raw_tick: dict) -> None:
            epoch: int = raw_tick["epoch"]
            quote_raw = raw_tick["quote"]
            quote = quote_raw if isinstance(quote_raw, Decimal) else Decimal(str(quote_raw))

            self._watchdog.mark(symbol)

            previous = self._last_epoch.get(symbol)
            self._last_epoch[symbol] = epoch
            if previous is not None and (epoch - previous) > gap_threshold:
                asyncio.create_task(self._heal_gap(symbol, previous))

            tick = Tick(
                symbol=symbol,
                epoch=epoch,
                quote=quote,
                digit=extract_digit(quote, meta.decimals),
            )
            await self._write_queue.put(tick)

        return handle

    async def _heal_gap(self, symbol: str, since_epoch: int) -> None:
        assert self._conn is not None and self._pool is not None
        meta = self._meta[symbol]
        written = await backfill_range(
            self._conn,
            self._pool,
            meta,
            start_epoch=since_epoch,
            page_size=self._settings.history_page_size,
        )
        if written:
            logger.info("in-stream gap healed for %s: %d ticks", symbol, written)

    async def _on_stale(self, symbol: str) -> None:
        assert self._conn is not None
        logger.warning("symbol %s stale, forcing reconnect", symbol)
        await self._conn.force_reconnect()

    async def _writer_loop(self) -> None:
        assert self._pool is not None
        batch: list[Tick] = []
        while True:
            try:
                tick = await asyncio.wait_for(
                    self._write_queue.get(), self._settings.write_batch_max_wait_seconds
                )
                batch.append(tick)
            except TimeoutError:
                pass

            should_flush = batch and (
                len(batch) >= self._settings.write_batch_max_size
                or self._write_queue.empty()
            )
            if should_flush:
                await insert_ticks(self._pool, batch)
                batch = []
