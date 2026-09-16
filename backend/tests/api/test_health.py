from app.api.routes import health
from tests.api.conftest import make_test_app


def test_healthz():
    client = make_test_app(health.router)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
