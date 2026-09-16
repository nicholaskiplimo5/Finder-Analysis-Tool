# Finder Analysis Tool

A statistical analysis dashboard for Deriv synthetic indices (digit and
tick streams). It measures whether patterns exist in data produced by a
cryptographically secure RNG — every statistic ships with a confidence
interval or p-value. **This is not a signal generator or trading tool**:
there is no buy endpoint, no auth token handling, and no real trading,
ever.

## Status

Early development. Current:
- Ingestion service (async Deriv WS client, reconnect/backoff, staleness
  watchdog, gap backfill, writes to Postgres).
- Analysis module (`backend/app/analysis/`): digit frequency + chi-square,
  ACF, conditional-probability matrix, streak lengths, rise/fall runs --
  pure numpy/scipy/statsmodels functions, windowed and cached, with
  multiple-comparison correction across symbols and lags.
- FastAPI layer (`backend/app/api/`) exposing the above as JSON, plus an
  SSE endpoint for live ticks.
- React dashboard (`frontend/`): frequency bars, ACF plot, conditional-
  probability heatmap, streak-length comparison, rise/fall summary, and
  a live tick feed. Every chart has a table-view twin and shows its
  p-value/CI directly in text -- nothing is color-coded as a signal.

## Local dev

```
cp .env.example .env   # fill in DERIV_APP_ID (register at api.deriv.com)
docker compose up
```

Dashboard at http://localhost:5173, API docs (Swagger UI) at
http://localhost:8000/docs, once the services are up.

For frontend-only iteration without Docker: `cd frontend && npm install
&& cp .env.example .env && npm run dev` (needs the `api` service running
separately, e.g. via `docker compose up postgres api`).

## License

This project is licensed under the terms of the [MIT License](LICENSE).
