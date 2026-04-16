# Akra Trader

Python-first trading research platform with hexagonal boundaries, a native runtime core, Binance-backed market data, and a control room for backtests, replay-based sandbox runs, and benchmark comparison.

## Current Status

Rebased to the repository state as of April 17, 2026.

What exists now:

- `apps/api`
  - FastAPI backend with domain/application/adapter separation
  - durable run storage through `SqlAlchemyRunRepository`
  - native backtest execution
  - replay-based sandbox preview flow for native strategies
  - Binance market-data adapter with sync, backfill, gap detection, and status reporting
  - reference catalog and Freqtrade-backed NostalgiaForInfinity backtest delegation
  - run comparison API with native vs reference benchmark support
- `apps/web`
  - React + TypeScript control room
  - strategy catalog, reference catalog, market-data status, backtest launch, sandbox launch/stop
  - run history filters and side-by-side comparison workflow
- `reference/NostalgiaForInfinity`
  - upstream reference repository kept as an external-runtime benchmark lane

What is still missing:

- continuous sandbox workers with heartbeat and restart recovery
- alerts, audit trail, and operator event history
- live execution adapters and hard guardrails
- durable strategy registration lifecycle beyond the current in-process catalog registration
- concrete LLM provider integration, trace storage, and replay tooling

## Strategy Model

The strategy boundary is intentionally broader than a single `buy` or `sell` hook.

Current stack:

1. `build_feature_frame`
2. `build_decision_context`
3. signal policy
4. execution policy
5. `StrategyDecisionEnvelope`

This keeps three lanes compatible with one orchestration model:

- native strategies
- Freqtrade reference strategies
- future `decision_engine` strategies

## Run Locally

### API

```bash
cd apps/api
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/uvicorn akra_trader.main:app --reload
```

Default behavior:

- runs are stored in `.local/state/runs.sqlite3`
- market data is stored in `.local/state/market-data.sqlite3`
- the default market-data provider is `binance`
- a background sync loop starts automatically when Binance is enabled

Useful overrides:

```bash
AKRA_TRADER_MARKET_DATA_PROVIDER=seeded
AKRA_TRADER_RUNS_DATABASE_URL=sqlite:////absolute/path/runs.sqlite3
AKRA_TRADER_MARKET_DATA_DATABASE_URL=sqlite:////absolute/path/market-data.sqlite3
```

### Web

```bash
cd apps/web
npm install
npm run dev
```

### Docker Compose

```bash
docker compose up --build
```

In the Compose stack, the API uses Postgres for run storage through
`AKRA_TRADER_RUNS_DATABASE_URL=postgresql+psycopg://akra:akra@postgres:5432/akra_trader`.

API default: `http://localhost:8000`

Web default: `http://localhost:5173`

## Tests

```bash
cd apps/api
.venv/bin/pytest
```

## NFI Reference Integration

The backend exposes upstream NFI strategies as catalog entries.

- `nfi_x7_reference`
- `nfi_next_reference`
- `nfi_nextgen_reference`

These entries point directly at files under [reference/NostalgiaForInfinity](/home/akra/dev/akra-trader/reference/NostalgiaForInfinity) and build Freqtrade backtest commands using upstream config conventions.

Current scope:

- backtest delegation is supported
- sandbox/live execution for reference strategies is not supported
- if `freqtrade` is unavailable, the prepared command and provenance are still recorded

## Reference Catalog

Third-party materials are tracked in [reference/catalog.toml](/home/akra/dev/akra-trader/reference/catalog.toml).

- `nostalgia-for-infinity`: external-runtime benchmark lane
- `nautilus-trader`: architecture reference only
- `ccxt`: direct dependency candidate used through adapters
- `yfinance`: direct dependency candidate

## Docs

- [Current State](docs/status/current-state.md)
- [Architecture](docs/architecture.md)
- [Roadmap Overview](docs/roadmap/README.md)
- [Product Roadmap](docs/roadmap/product-roadmap.md)
- [Technical Roadmap](docs/roadmap/technical-roadmap.md)
- [Epic Backlog](docs/roadmap/epic-backlog.md)
- [ADR Index](docs/adr/README.md)
- [NautilusTrader Notes](docs/reference-nautilus-trader.md)
- [NostalgiaForInfinity Notes](docs/reference-nostalgia-for-infinity.md)
