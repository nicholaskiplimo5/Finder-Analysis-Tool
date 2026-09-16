from app.api.routes import conditional_digit as conditional_digit_routes
from tests.api.conftest import make_test_app
from tests.api.fakes import FakeConditionalDigitService
from tests.api.settings_helper import make_settings


def test_get_conditional_digit_single_symbol():
    client = make_test_app(
        conditional_digit_routes.router,
        conditional_digit_service=FakeConditionalDigitService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/conditional-digit/R_100")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["counts"]) == 10
    assert len(body["counts"][0]) == 10
    assert body["degrees_of_freedom"] == 81


def test_get_conditional_digit_unknown_symbol_404():
    client = make_test_app(
        conditional_digit_routes.router,
        conditional_digit_service=FakeConditionalDigitService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/conditional-digit/NOPE")
    assert resp.status_code == 404


def test_get_conditional_digit_value_error_maps_to_400():
    client = make_test_app(
        conditional_digit_routes.router,
        conditional_digit_service=FakeConditionalDigitService(raise_error=ValueError("bad")),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/conditional-digit/R_100")
    assert resp.status_code == 400


def test_get_conditional_digit_summary_applies_correction():
    client = make_test_app(
        conditional_digit_routes.router,
        conditional_digit_service=FakeConditionalDigitService(),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/conditional-digit")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body["results"].keys()) == {"R_100", "R_10"}
    assert body["correction"]["method"] == "holm"
    assert body["skipped"] == {}


def test_get_conditional_digit_summary_skips_symbols_without_data():
    client = make_test_app(
        conditional_digit_routes.router,
        conditional_digit_service=FakeConditionalDigitService(skipped_symbols=["R_10"]),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/conditional-digit")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body["results"].keys()) == {"R_100"}
    assert list(body["skipped"].keys()) == ["R_10"]


def test_get_conditional_digit_summary_400s_when_every_symbol_skipped():
    client = make_test_app(
        conditional_digit_routes.router,
        conditional_digit_service=FakeConditionalDigitService(skipped_symbols=["R_100", "R_10"]),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/conditional-digit")
    assert resp.status_code == 400
