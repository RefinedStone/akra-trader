# Akra Trader

Single-operator trading research workstation.

`akra-trader` is crypto-first today. It combines durable research runs, market-data lineage,
benchmark comparison, sandbox workers, and guarded-live control surfaces in one control room.

## Product Read

Implemented:

- native strategy catalog, backtests, run history, rerun boundaries, presets, and comparisons
- market-data sync status, lineage history, gap/failure visibility, and drill evidence exports
- sandbox and paper sessions with persisted heartbeat, progress, and recovery state
- guarded-live gates, kill switch, reconciliation, recovery, order cancel/replace, incidents, and
  delivery history
- route-aware React control room with split API/type barrels and feature-owned query/run-history
  modules

Still incomplete:

- durable custom strategy lifecycle and promotion workflow
- normalized experiment artifact/export storage for every common query path
- full venue-native live lifecycle recovery and deployment/secret governance
- simpler active-session operator UX across all runtime and live workflows
- traceable LLM research infrastructure beyond the current port/interface shape

## Run Locally

API:

```bash
cd apps/api
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/uvicorn akra_trader.main:app --reload
```

Web:

```bash
cd apps/web
npm install
npm run dev
```

Docker Compose:

```bash
docker compose up --build
```

Default URLs:

- API: `http://localhost:8000`
- Web: `http://localhost:5173`
- Compose API: `http://localhost:47680`
- Compose Web: `http://localhost:47613`

## Checks

```bash
cd apps/api
.venv/bin/pytest
```

```bash
cd apps/web
npm run typecheck
```

## Documentation

- [docs/README.md](docs/README.md): compact documentation map
- [Current State](docs/status/current-state.md): canonical implementation snapshot
- [Architecture](docs/architecture.md): current boundaries and pressure points
- [Roadmap](docs/roadmap/README.md): remaining work
- [Operations](docs/operations/runbooks-overview.md): compact operator checklist
- [Blueprint](docs/blueprint/README.md): long-horizon principles only
- [ADR Index](docs/adr/README.md): historical decisions
