from decimal import Decimal

from app.ingestion.deriv_ws import DerivConnection
from app.ingestion.digits import decimals_from_pip_size
from app.models import SymbolMeta


async def fetch_symbol_meta(
    conn: DerivConnection, symbols: list[str]
) -> dict[str, SymbolMeta]:
    response = await conn.send_request({"active_symbols": "brief"})
    by_symbol = {row["symbol"]: row for row in response["active_symbols"]}

    missing = [s for s in symbols if s not in by_symbol]
    if missing:
        raise ValueError(f"symbols not found in active_symbols: {missing}")

    result: dict[str, SymbolMeta] = {}
    for symbol in symbols:
        pip_size = Decimal(str(by_symbol[symbol]["pip"]))
        decimals = decimals_from_pip_size(pip_size)
        result[symbol] = SymbolMeta(symbol=symbol, pip_size=pip_size, decimals=decimals)
    return result
