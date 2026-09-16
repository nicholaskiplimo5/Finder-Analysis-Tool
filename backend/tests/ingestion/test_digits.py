from decimal import Decimal

import pytest

from app.ingestion.digits import (
    decimals_from_pip_size,
    expected_interval_seconds,
    extract_digit,
    parse_deriv_message,
)


@pytest.mark.parametrize(
    "pip_size, expected",
    [
        (Decimal("0.01"), 2),
        (Decimal("0.001"), 3),
        (Decimal("0.0001"), 4),
        (Decimal("0.00001"), 5),
        (Decimal("1"), 0),
    ],
)
def test_decimals_from_pip_size(pip_size, expected):
    assert decimals_from_pip_size(pip_size) == expected


def test_extract_digit_preserves_trailing_zero():
    # The actual trap: a quote that is a whole "tenth" (1234.60) must read
    # its last digit as 0, not silently collapse to the shorter value
    # (1234.6) and read 6.
    assert extract_digit(Decimal("1234.60"), decimals=2) == 0
    assert extract_digit(Decimal("1234.6"), decimals=2) == 0


def test_extract_digit_basic_cases():
    assert extract_digit(Decimal("1234.56"), decimals=2) == 6
    assert extract_digit(Decimal("1234.50"), decimals=2) == 0
    assert extract_digit(Decimal("1234.501"), decimals=3) == 1
    assert extract_digit(Decimal("100"), decimals=0) == 0
    assert extract_digit(Decimal("109"), decimals=0) == 9


def test_parse_deriv_message_does_not_go_through_binary_float():
    # If this were decoded with the default json float handling, the
    # value would round-trip through IEEE754 double before ever reaching
    # our Decimal logic, reopening the exact trap extract_digit guards
    # against. Asserting the parsed type is Decimal (not float) is the
    # regression test for that.
    raw = '{"msg_type": "tick", "tick": {"symbol": "R_100", "epoch": 100, "quote": 1234.60}}'
    msg = parse_deriv_message(raw)
    quote = msg["tick"]["quote"]
    assert isinstance(quote, Decimal)
    assert extract_digit(quote, decimals=2) == 0


@pytest.mark.parametrize(
    "symbol, expected",
    [
        ("R_10", 2.0),
        ("R_100", 2.0),
        ("1HZ10V", 1.0),
        ("1HZ100V", 1.0),
    ],
)
def test_expected_interval_seconds(symbol, expected):
    assert expected_interval_seconds(symbol) == expected
