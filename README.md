# Akra Trader

Python-first algorithmic trading platform with strong hexagonal boundaries, an operations dashboard, a native strategy engine, and direct NostalgiaForInfinity reference integration.

## What exists now

- `apps/api`
  - FastAPI backend
  - hexagonal domain/application/adapter split
  - native backtest and paper-replay engine
  - strategy pipeline split into `feature frame -> decision context -> decision envelope`
  - NFI reference catalog and Freqtrade command delegation
- `apps/web`
  - React + TypeScript control room
  - strategy catalog, market-data status, backtest launch, paper run control
- `reference/NostalgiaForInfinity`
  - upstream reference repository kept intact for strategy/config reuse

## Why the strategy layering matters

The strategy boundary is intentionally more abstract than a typical "indicator in, buy/sell out" interface.

Current stack:

1. `build_feature_frame`
2. `build_decision_context`
3. `decide`
4. execution engine applies the returned signal

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

### Web

```bash
cd apps/web
npm install
npm run dev
```

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

## Docs

- [Architecture](docs/architecture.md)
- [Roadmap Overview](docs/roadmap/README.md)
- [Product Roadmap](docs/roadmap/product-roadmap.md)
- [Technical Roadmap](docs/roadmap/technical-roadmap.md)
- [Epic Backlog](docs/roadmap/epic-backlog.md)
- [ADR Index](docs/adr/README.md)
