import pytest

from app.ingestion.watchdog import StalenessWatchdog, make_threshold_fn


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


@pytest.mark.asyncio
async def test_symbol_not_stale_before_threshold():
    clock = FakeClock()
    fired = []

    async def on_stale(symbol):
        fired.append(symbol)

    wd = StalenessWatchdog(
        ["R_100"], threshold_seconds=lambda s: 10.0, on_stale=on_stale, clock=clock
    )
    wd.mark("R_100")
    clock.advance(9.0)

    stale = await wd.check_once()
    assert stale == []
    assert fired == []


@pytest.mark.asyncio
async def test_symbol_stale_after_threshold_fires_callback():
    clock = FakeClock()
    fired = []

    async def on_stale(symbol):
        fired.append(symbol)

    wd = StalenessWatchdog(
        ["R_100"], threshold_seconds=lambda s: 10.0, on_stale=on_stale, clock=clock
    )
    wd.mark("R_100")
    clock.advance(11.0)

    stale = await wd.check_once()
    assert stale == ["R_100"]
    assert fired == ["R_100"]


@pytest.mark.asyncio
async def test_unmarked_symbol_never_flagged_stale():
    # A symbol that hasn't been marked yet (never subscribed, or just
    # resubscribed and no tick has arrived yet) should not be treated as
    # stale -- it hasn't had a chance to prove itself alive or dead.
    clock = FakeClock()
    fired = []

    async def on_stale(symbol):
        fired.append(symbol)

    wd = StalenessWatchdog(
        ["R_100"], threshold_seconds=lambda s: 10.0, on_stale=on_stale, clock=clock
    )
    clock.advance(1000.0)

    stale = await wd.check_once()
    assert stale == []
    assert fired == []


@pytest.mark.asyncio
async def test_firing_resets_timer_to_avoid_refiring_every_check():
    clock = FakeClock()
    fired = []

    async def on_stale(symbol):
        fired.append(symbol)

    wd = StalenessWatchdog(
        ["R_100"], threshold_seconds=lambda s: 10.0, on_stale=on_stale, clock=clock
    )
    wd.mark("R_100")
    clock.advance(11.0)
    await wd.check_once()
    assert fired == ["R_100"]

    # Immediately check again without the symbol recovering (no new mark).
    # It should not refire until another full threshold has elapsed.
    stale = await wd.check_once()
    assert stale == []
    assert fired == ["R_100"]


def test_make_threshold_fn_applies_multiplier_and_floor():
    threshold = make_threshold_fn(lambda s: 1.0, multiplier=6.0, floor_seconds=10.0)
    assert threshold("1HZ10V") == 10.0  # floor wins: 1.0 * 6 = 6 < 10

    threshold2 = make_threshold_fn(lambda s: 2.0, multiplier=6.0, floor_seconds=10.0)
    assert threshold2("R_100") == 12.0  # multiplier wins: 2.0 * 6 = 12 > 10
