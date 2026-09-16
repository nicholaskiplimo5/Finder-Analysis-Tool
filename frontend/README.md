# Finder Analysis Tool -- frontend

React + TypeScript dashboard (module 4). Consumes the FastAPI backend in
`../backend` -- see the root README for the full-stack `docker compose up`
workflow.

## Stack

- Vite + React + TypeScript
- Recharts for charts, TanStack Query for data fetching/caching
- Tailwind CSS v4
- Vitest + React Testing Library

## Local dev (frontend only)

```
npm install
cp .env.example .env   # VITE_API_BASE_URL, defaults to http://localhost:8000
npm run dev
```

Needs a running backend to talk to -- `docker compose up postgres api` from
the repo root, or `main_api.py`/`uvicorn app.api.app:app` directly.

## Scripts

- `npm run dev` -- dev server
- `npm run build` -- typecheck + production build
- `npm test` -- Vitest
- `npm run lint` -- oxlint

## Structure

- `src/api/` -- typed API client, TanStack Query hooks, the SSE live-tick hook
- `src/components/` -- one component per chart/stat, each with a sibling
  `*.transforms.ts` holding the pure API-response-to-chart-row function
  (unit tested independently of rendering)
- `src/lib/` -- formatting and color helpers

Every chart has a "Table" view twin, holds its previous render at reduced
opacity while refetching (no skeleton flash), and states its p-value in
plain text rather than color-coding significance -- this tool measures
randomness, it does not recommend trades.
