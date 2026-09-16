"""Decimal-safe parsing and last-digit extraction.

The trap: Deriv sends quotes as JSON numbers already formatted to the
symbol's pip size (e.g. 1234.60). If those numbers are decoded through
Python's default `json` float handling and then re-stringified naively
(`str(1234.6)` -> "1234.6"), the trailing zero is lost and the last digit
read as 6 instead of the correct 0. Any statistic built on that digit
stream is measuring a formatting artifact, not the RNG.

The fix has two parts:
  1. Decode JSON with `parse_float=Decimal` so numeric fields never pass
     through a binary float at all.
  2. Re-quantize to the symbol's known decimal places (from pip_size)
     before reading the last character, so a trailing zero the wire
     format carried is preserved even if some upstream value has fewer
     printed digits than expected.
"""

import json
from decimal import Decimal


def parse_deriv_message(raw: str | bytes) -> dict:
    """Decode a Deriv WS frame preserving exact decimal precision."""
    return json.loads(raw, parse_float=Decimal)


def decimals_from_pip_size(pip_size: Decimal) -> int:
    """Number of decimal places implied by a pip size like 0.01 -> 2."""
    exponent = pip_size.normalize().as_tuple().exponent
    if not isinstance(exponent, int):
        raise ValueError(f"non-finite pip_size: {pip_size}")
    return max(-exponent, 0)


def extract_digit(quote: Decimal, decimals: int) -> int:
    """Last decimal digit of `quote`, formatted to exactly `decimals` places."""
    quantum = Decimal(1).scaleb(-decimals)
    quantized = quote.quantize(quantum)
    formatted = f"{quantized:.{decimals}f}" if decimals > 0 else f"{quantized:.0f}"
    return int(formatted[-1])


# Deriv does not expose tick cadence via active_symbols; this is a
# hardcoded assumption based on the documented symbol families and should
# be revisited if a symbol outside these two patterns is added.
def expected_interval_seconds(symbol: str) -> float:
    return 1.0 if symbol.startswith("1HZ") else 2.0
