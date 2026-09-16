from app.api.routes import digit_frequency as digit_frequency_routes
from tests.api.conftest import make_test_app
from tests.api.fakes import FakeDigitFrequencyService
from tests.api.settings_helper import make_settings


def test_get_digit_frequency_single_symbol():
    client = make_test_app(
        digit_frequency_routes.router,
        digit_frequency_service=FakeDigitFrequencyService(),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/digit-frequency/R_100")

    assert resp.status_code == 200
    body = resp.json()
    assert body["n"] == 1000
    assert len(body["observed_counts"]) == 10
    assert body["p_value"] == 1.0


def test_get_digit_frequency_unknown_symbol_404():
    client = make_test_app(
        digit_frequency_routes.router,
        digit_frequency_service=FakeDigitFrequencyService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/digit-frequency/NOT_A_SYMBOL")
    assert resp.status_code == 404


def test_get_digit_frequency_value_error_maps_to_400():
    client = make_test_app(
        digit_frequency_routes.router,
        digit_frequency_service=FakeDigitFrequencyService(raise_error=ValueError("window too small")),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/digit-frequency/R_100")

    assert resp.status_code == 400
    assert resp.json() == {"detail": "window too small"}


def test_get_digit_frequency_summary_applies_correction():
    client = make_test_app(
        digit_frequency_routes.router,
        digit_frequency_service=FakeDigitFrequencyService(),
        settings=make_settings(symbols="R_100,R_10"),
    )
    resp = client.get("/api/digit-frequency")

    assert resp.status_code == 200
    body = resp.json()
    assert set(body["results"].keys()) == {"R_100", "R_10"}
    assert body["correction"]["method"] == "holm"
    assert len(body["correction"]["corrected_p_values"]) == 2


def test_window_query_param_out_of_bounds_rejected():
    client = make_test_app(
        digit_frequency_routes.router,
        digit_frequency_service=FakeDigitFrequencyService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/digit-frequency/R_100?window=10")  # below ge=100
    assert resp.status_code == 422
