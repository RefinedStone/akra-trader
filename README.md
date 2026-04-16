# Akra Trader

Python-first algorithmic trading platform with strong hexagonal boundaries, an operations dashboard, a native strategy engine, and direct NostalgiaForInfinity reference integration.

## What exists now

- `apps/api`
  - FastAPI backend
  - hexagonal domain/application/adapter split
  - native backtest and sandbox-replay engine
  - strategy pipeline split into `feature frame -> decision context -> signal policy -> execution policy -> decision envelope`
  - reference catalog, NFI Freqtrade delegation, and run provenance capture
- `apps/web`
  - React + TypeScript control room
  - strategy catalog, reference catalog, market-data status, backtest launch, sandbox run control
- `reference/NostalgiaForInfinity`
  - upstream reference repository kept intact for strategy/config reuse

## Why the strategy layering matters

The strategy boundary is intentionally more abstract than a typical "indicator in, buy/sell out" interface.

Current stack:

1. `build_feature_frame`
2. `build_decision_context`
3. `signal_policy`
4. `execution_policy`
5. execution engine applies the returned intent

This lets three strategy families coexist:

- native rule-based strategies
- Freqtrade/NFI reference strategies
- future LLM-driven strategies that delegate `decide()` to an external decision engine

## Run locally

### API

```bash
cd apps/api
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/uvicorn akra_trader.main:app --reload
```

Run storage defaults to a local SQLite file under `.local/state/runs.sqlite3`.

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
.venv/bin/python -m pytest
```

## NFI reference integration

The backend now exposes upstream NFI strategies as catalog entries.

- `nfi_x7_reference`
- `nfi_next_reference`
- `nfi_nextgen_reference`

These entries point directly at files under [reference/NostalgiaForInfinity](/home/akra/dev/akra-trader/reference/NostalgiaForInfinity) and build Freqtrade commands using the same config patterns found in the upstream test helpers.

If `freqtrade` is not installed, the platform records the prepared command and reports that the reference runtime is unavailable.

## Reference catalog

Third-party materials are tracked in [reference/catalog.toml](/home/akra/dev/akra-trader/reference/catalog.toml).

- `nostalgia-for-infinity`: external-runtime reference lane
- `nautilus-trader`: ideas-only architecture reference
- `ccxt`: direct dependency candidate for exchange adapters
- `yfinance`: direct dependency candidate for stock-market data

## Docs

- [Architecture](docs/architecture.md)
- [NautilusTrader Notes](docs/reference-nautilus-trader.md)
- [NostalgiaForInfinity Notes](docs/reference-nostalgia-for-infinity.md)
- [Roadmap Overview](docs/roadmap/README.md)
- [Product Roadmap](docs/roadmap/product-roadmap.md)
- [Technical Roadmap](docs/roadmap/technical-roadmap.md)
- [Epic Backlog](docs/roadmap/epic-backlog.md)
- [ADR Index](docs/adr/README.md)
