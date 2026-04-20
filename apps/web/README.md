# Akra Trader Web

React + TypeScript control room for `akra-trader`.

Updated for the repository state as of April 21, 2026.

## Current Scope

The web app already covers more than a backtest launcher.

Implemented now:

- strategy catalog grouped by runtime lane
- reference catalog and benchmark context
- market-data health, gap, backfill, and sync summaries
- backtest, sandbox, and guarded-live launch flows
- separate histories for backtest, sandbox, paper, and live modes
- side-by-side comparison and benchmark narratives
- guarded-live alerts, incidents, delivery history, kill switch, reconciliation, and recovery panels
- replay-link alias governance and audit administration surfaces

Current product limit:

- the control room is still a large single-screen application and needs clearer decomposition into
  research, active-runtime, and guarded-live workflows

## Run

```bash
npm install
npm run dev
```

The app reads `VITE_API_BASE_URL` and defaults to `http://localhost:8000/api`.
