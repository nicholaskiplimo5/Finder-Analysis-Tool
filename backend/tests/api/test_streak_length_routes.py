from app.api.routes import streak_length as streak_length_routes
from tests.api.conftest import make_test_app
from tests.api.fakes import FakeStreakLengthService
from tests.api.settings_helper import make_settings


def test_get_streak_length_single_symbol():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/streak-length/R_100")

    assert resp.status_code == 200
    body = resp.json()
    assert body["bin_labels"] == ["1", "2", "3", ">=4"]
    assert body["n_streaks"] == 900


def test_get_streak_length_unknown_symbol_404():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/streak-length/NOPE")
    assert resp.status_code == 404


def test_get_streak_length_value_error_maps_to_400():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(raise_error=ValueError("bad")),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/streak-length/R_100")
    assert resp.status_code == 400


def test_max_bin_query_param_out_of_bounds_rejected():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/streak-length/R_100?max_bin=1")  # ge=2
    assert resp.status_code == 422


def test_get_streak_length_summary_applies_correction():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/streak-length")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body["results"].keys()) == {"R_100", "R_10"}
    assert body["skipped"] == {}


def test_get_streak_length_summary_skips_symbols_without_data():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(skipped_symbols=["R_10"]),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/streak-length")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body["results"].keys()) == {"R_100"}
    assert list(body["skipped"].keys()) == ["R_10"]


def test_get_streak_length_summary_400s_when_every_symbol_skipped():
    client = make_test_app(
        streak_length_routes.router,
        streak_length_service=FakeStreakLengthService(skipped_symbols=["R_100", "R_10"]),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/streak-length")
    assert resp.status_code == 400
