from app.api.routes import acf as acf_routes
from tests.api.conftest import make_test_app
from tests.api.fakes import FakeACFService
from tests.api.settings_helper import make_settings


def test_get_acf_single_symbol():
    client = make_test_app(
        acf_routes.router,
        acf_service=FakeACFService(max_lag=5),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/acf/R_100?max_lag=5")

    assert resp.status_code == 200
    body = resp.json()
    assert body["acf"]["max_lag"] == 5
    assert len(body["acf"]["lags"]) == 5
    assert body["lag_correction"]["method"] == "holm"
    assert len(body["lag_correction"]["corrected_p_values"]) == 5


def test_get_acf_unknown_symbol_404():
    client = make_test_app(
        acf_routes.router,
        acf_service=FakeACFService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/acf/NOPE")
    assert resp.status_code == 404


def test_get_acf_value_error_maps_to_400():
    client = make_test_app(
        acf_routes.router,
        acf_service=FakeACFService(raise_error=ValueError("bad window")),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/acf/R_100")
    assert resp.status_code == 400


def test_max_lag_query_param_out_of_bounds_rejected():
    client = make_test_app(
        acf_routes.router,
        acf_service=FakeACFService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/acf/R_100?max_lag=0")  # ge=1
    assert resp.status_code == 422


def test_no_multi_symbol_acf_endpoint():
    # Deliberate: ACF has no natural single p-value per symbol to correct
    # across symbols (see acf.py's module docstring/comment), so "" isn't
    # a registered route the way it is for the other four stats.
    client = make_test_app(
        acf_routes.router,
        acf_service=FakeACFService(),
        settings=make_settings(symbols="R_100"),
    )
    resp = client.get("/api/acf")
    assert resp.status_code == 404
