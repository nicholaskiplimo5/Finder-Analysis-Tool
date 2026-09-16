"""Build a minimal FastAPI app around fake services for route-level
tests -- no real Settings(), no real DB pool, no lifespan. Route code
only ever reads from `request.app.state`, so tests populate that state
directly with fakes instead of exercising the real DB-backed services
(same "pure logic tested, DB layer thin" split as modules 1 and 2)."""

from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.api.errors import install_error_handlers


def make_test_app(*routers: APIRouter, **state: object) -> TestClient:
    app = FastAPI()
    install_error_handlers(app)
    for router in routers:
        app.include_router(router)
    for key, value in state.items():
        setattr(app.state, key, value)
    return TestClient(app)
