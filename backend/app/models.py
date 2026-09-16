from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class SymbolMeta:
    symbol: str
    pip_size: Decimal
    decimals: int


@dataclass(frozen=True, slots=True)
class Tick:
    symbol: str
    epoch: int
    quote: Decimal
    digit: int
