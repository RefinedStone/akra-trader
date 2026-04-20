# Akra Trader

Python-first trading research workstation for a single operator.

`akra-trader` combines durable research runs, benchmark comparison, sandbox worker supervision,
and guarded-live safety surfaces behind one control room. The repository is crypto-first today and
keeps extension paths open for additional venues and future intelligence-assisted research.

## Current Product Position

Updated for the repository state as of April 21, 2026.

The project is no longer only a backtest playground. It already includes:

- durable native backtests with dataset lineage and rerun boundaries
- native vs reference benchmark comparison with stored provenance
- experiment presets, richer query/filter surfaces, and replay-link audit utilities
- supervised sandbox worker sessions with heartbeat and restart recovery
- guarded-live kill switch, reconciliation, recovery, and venue-backed launch gates
- operator visibility, incident history, delivery history, and guarded-live control surfaces

The project is not yet:

- a fully productized live trading workstation
- a multi-user or RBAC-enabled platform
- a complete experiment OS with durable custom strategy registration and rich artifact storage
- a traceable LLM research lane with replay, fallback, and provider adapters

## Run Locally

### API

```bash
cd apps/api
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/uvicorn akra_trader.main:app --reload
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

API default: `http://localhost:8000`

Web default: `http://localhost:5173`

## Tests

```bash
cd apps/api
.venv/bin/pytest
```

```bash
cd apps/web
npm run typecheck
```

## Repository Guide

- [docs/README.md](docs/README.md): documentation index and reading order
- [docs/status/current-state.md](docs/status/current-state.md): canonical current-state document
- [docs/status/product-position.md](docs/status/product-position.md): what product this is today
- [docs/roadmap/README.md](docs/roadmap/README.md): remaining work overview
- [docs/roadmap/next-wave-plan.md](docs/roadmap/next-wave-plan.md): detailed next-wave execution plan
- [docs/architecture.md](docs/architecture.md): architectural shape and boundary rules
- [docs/blueprint/README.md](docs/blueprint/README.md): longer-horizon blueprint and gate documents

## Reference Lanes

Third-party materials are tracked in `reference/catalog.toml`.

- `nostalgia-for-infinity`: external-runtime benchmark lane
- `nautilus-trader`: architecture reference
- `ccxt`: adapter dependency candidate already used in market-data and venue-facing layers
- `yfinance`: future direct dependency candidate

Freqtrade-backed reference backtests are available through the NFI catalog entries. Sandbox and
guarded-live execution remain native-only today.
