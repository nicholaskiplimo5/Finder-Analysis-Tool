from decimal import Decimal

from app.api.routes import symbols as symbols_routes
from app.models import SymbolMeta
from tests.api.conftest import make_test_app


def test_list_symbols(monkeypatch):
    async def fake_fetch_all_symbol_meta(pool):
        return [SymbolMeta(symbol="R_100", pip_size=Decimal("0.01"), decimals=2)]

    monkeypatch.setattr(symbols_routes, "fetch_all_symbol_meta", fake_fetch_all_symbol_meta)

    client = make_test_app(symbols_routes.router, pool=object())
    resp = client.get("/api/symbols")

    assert resp.status_code == 200
    assert resp.json() == [{"symbol": "R_100", "pip_size": "0.01", "decimals": 2}]


def test_list_symbols_empty(monkeypatch):
    async def fake_fetch_all_symbol_meta(pool):
        return []

    monkeypatch.setattr(symbols_routes, "fetch_all_symbol_meta", fake_fetch_all_symbol_meta)

    client = make_test_app(symbols_routes.router, pool=object())
    resp = client.get("/api/symbols")

    assert resp.status_code == 200
    assert resp.json() == []
