# Finder Analysis Tool

A statistical analysis dashboard for Deriv synthetic indices (digit and
tick streams). It measures whether patterns exist in data produced by a
cryptographically secure RNG — every statistic ships with a confidence
interval or p-value. **This is not a signal generator or trading tool**:
there is no buy endpoint, no auth token handling, and no real trading,
ever.

## Status

Early development. Current: ingestion service (async Deriv WS client,
reconnect/backoff, staleness watchdog, gap backfill, writes to Postgres).
See `backend/`.

## Local dev

```
cp .env.example .env   # fill in DERIV_APP_ID (register at api.deriv.com)
docker compose up
```

## License

This project is licensed under the terms of the [MIT License](LICENSE).
