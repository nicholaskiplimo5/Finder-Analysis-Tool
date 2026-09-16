from app.api.routes import rise_fall as rise_fall_routes
from tests.api.conftest import make_test_app
from tests.api.fakes import FakeRiseFallService
from tests.api.settings_helper import make_settings


def test_get_rise_fall_single_symbol():
    client = make_test_app(
        rise_fall_routes.router,
        rise_fall_service=FakeRiseFallService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/rise-fall/R_100")

    assert resp.status_code == 200
    body = resp.json()
    assert body["n_rises"] == 500
    assert body["n_falls"] == 499


def test_get_rise_fall_unknown_symbol_404():
    client = make_test_app(
        rise_fall_routes.router,
        rise_fall_service=FakeRiseFallService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/rise-fall/NOPE")
    assert resp.status_code == 404


def test_get_rise_fall_value_error_maps_to_400():
    client = make_test_app(
        rise_fall_routes.router,
        rise_fall_service=FakeRiseFallService(raise_error=ValueError("bad")),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/rise-fall/R_100")
    assert resp.status_code == 400


def test_get_rise_fall_summary_applies_correction():
    client = make_test_app(
        rise_fall_routes.router,
        rise_fall_service=FakeRiseFallService(),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/rise-fall")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body["results"].keys()) == {"R_100", "R_10"}
    assert body["correction"]["method"] == "holm"
