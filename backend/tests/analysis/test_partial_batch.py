import pytest

from app.analysis.partial_batch import run_partial_batch


@pytest.mark.asyncio
async def test_all_succeed():
    async def get_one(symbol):
        return f"result-{symbol}"

    results, skipped = await run_partial_batch(["A", "B"], get_one)

    assert results == {"A": "result-A", "B": "result-B"}
    assert skipped == {}


@pytest.mark.asyncio
async def test_some_fail_with_value_error_are_skipped_not_raised():
    async def get_one(symbol):
        if symbol == "B":
            raise ValueError("no ticks stored")
        return f"result-{symbol}"

    results, skipped = await run_partial_batch(["A", "B", "C"], get_one)

    assert results == {"A": "result-A", "C": "result-C"}
    assert skipped == {"B": "no ticks stored"}


@pytest.mark.asyncio
async def test_all_fail_yields_empty_results_not_an_exception():
    async def get_one(symbol):
        raise ValueError(f"no ticks stored for {symbol}")

    results, skipped = await run_partial_batch(["A", "B"], get_one)

    assert results == {}
    assert skipped == {"A": "no ticks stored for A", "B": "no ticks stored for B"}


@pytest.mark.asyncio
async def test_non_value_error_propagates_instead_of_being_skipped():
    async def get_one(symbol):
        raise RuntimeError("db connection lost")

    with pytest.raises(RuntimeError):
        await run_partial_batch(["A"], get_one)


@pytest.mark.asyncio
async def test_empty_symbol_list():
    async def get_one(symbol):
        return symbol

    results, skipped = await run_partial_batch([], get_one)

    assert results == {}
    assert skipped == {}
