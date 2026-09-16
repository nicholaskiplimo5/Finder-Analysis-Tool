from app.config import Settings


def make_settings(**overrides) -> Settings:
    defaults = {"deriv_app_id": "x", "database_url": "postgresql://x/x"}
    return Settings(**{**defaults, **overrides})
