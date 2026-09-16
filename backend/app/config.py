from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    deriv_app_id: str
    database_url: str

    symbols: list[str] = [
        "R_10", "R_25", "R_50", "R_75", "R_100",
        "1HZ10V", "1HZ25V", "1HZ50V", "1HZ75V", "1HZ100V",
    ]

    ping_interval_seconds: float = 25.0
    request_timeout_seconds: float = 10.0

    reconnect_backoff_base_seconds: float = 1.0
    reconnect_backoff_max_seconds: float = 60.0

    history_page_size: int = 5000
    cold_start_backfill_count: int = 50_000

    watchdog_check_interval_seconds: float = 5.0
    staleness_multiplier: float = 6.0
    staleness_floor_seconds: float = 10.0

    # Multiple of a symbol's expected tick interval beyond which an
    # in-stream epoch jump is treated as a gap to heal, rather than
    # ordinary network jitter.
    gap_multiplier: float = 1.5

    write_batch_max_size: int = 200
    write_batch_max_wait_seconds: float = 1.0

    # API layer (module 3). Read by the ingestion process too since both
    # share this Settings class and one .env -- unused there, harmless.
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    live_tick_poll_interval_seconds: float = 1.0

    @property
    def deriv_ws_url(self) -> str:
        return f"wss://ws.derivws.com/websockets/v3?app_id={self.deriv_app_id}"

    @field_validator("symbols", "cors_origins", mode="before")
    @classmethod
    def _split_csv(cls, value: object) -> object:
        if isinstance(value, str):
            return [s.strip() for s in value.split(",") if s.strip()]
        return value
