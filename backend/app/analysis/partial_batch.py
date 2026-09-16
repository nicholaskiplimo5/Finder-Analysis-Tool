"""Run an async per-symbol computation across many symbols, tolerating
individual failures instead of letting one bad symbol take down the
whole batch.

Used by every stat service's get_many: a symbol still mid cold-start
backfill (or newly added to config) raises ValueError from its own
get() just like a single-symbol request would -- but a summary endpoint
scanning all symbols shouldn't 400 in its entirety just because one
symbol isn't ready yet.
"""

from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def run_partial_batch(
    symbols: list[str], get_one: Callable[[str], Awaitable[T]]
) -> tuple[dict[str, T], dict[str, str]]:
    """Returns (results, skipped): `skipped` maps a symbol to the
    str(ValueError) that excluded it from `results`. Errors other than
    ValueError are not caught here -- those are bugs or infrastructure
    failures, not "this symbol isn't ready yet", and should surface as a
    real 500 rather than being silently swallowed into a skip list."""
    results: dict[str, T] = {}
    skipped: dict[str, str] = {}
    for symbol in symbols:
        try:
            results[symbol] = await get_one(symbol)
        except ValueError as e:
            skipped[symbol] = str(e)
    return results, skipped
