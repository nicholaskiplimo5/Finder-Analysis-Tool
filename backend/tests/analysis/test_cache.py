import pytest

from app.analysis.cache import WindowedStatCache


@pytest.mark.asyncio
async def test_reuses_cached_result_when_version_unchanged():
    calls = []

    async def compute():
        calls.append(1)
        return len(calls)

    cache = WindowedStatCache()
    first = await cache.get_or_compute("k", version=1, compute=compute)
    second = await cache.get_or_compute("k", version=1, compute=compute)

    assert first == 1
    assert second == 1
    assert len(calls) == 1  # compute only ran once


@pytest.mark.asyncio
async def test_recomputes_when_version_advances():
    calls = []

    async def compute():
        calls.append(1)
        return len(calls)

    cache = WindowedStatCache()
    first = await cache.get_or_compute("k", version=1, compute=compute)
    second = await cache.get_or_compute("k", version=2, compute=compute)

    assert first == 1
    assert second == 2
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_different_keys_are_independent():
    async def compute_a():
        return "a-result"

    async def compute_b():
        return "b-result"

    cache = WindowedStatCache()
    a = await cache.get_or_compute(("sym", 100), version=5, compute=compute_a)
    b = await cache.get_or_compute(("sym", 200), version=5, compute=compute_b)

    assert a == "a-result"
    assert b == "b-result"


@pytest.mark.asyncio
async def test_invalidate_forces_recompute():
    calls = []

    async def compute():
        calls.append(1)
        return len(calls)

    cache = WindowedStatCache()
    await cache.get_or_compute("k", version=1, compute=compute)
    cache.invalidate("k")
    result = await cache.get_or_compute("k", version=1, compute=compute)

    assert result == 2
    assert len(calls) == 2
