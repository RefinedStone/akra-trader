# Akra Trader Web

React + TypeScript control room for inspecting strategy lanes, market-data health, run history, and benchmark comparisons.

## Current Scope

Implemented now:

- strategy catalog grouped by runtime lane
- reference catalog display
- market-data status board with backfill and gap summaries
- backtest launch form
- native sandbox launch and stop controls
- backtest and sandbox run history filters
- side-by-side backtest comparison with benchmark narratives

Important current limit:

- the sandbox view controls replay-based preview runs, not continuous real-time workers

## Run

```bash
npm install
npm run dev
```

The app reads `VITE_API_BASE_URL` and defaults to `http://localhost:8000/api`.
