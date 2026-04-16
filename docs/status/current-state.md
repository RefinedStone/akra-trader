# Current State

Canonical status snapshot for the repository as of April 17, 2026.

Use this document as the source of truth for "what exists now" before reading roadmap or architecture docs.

Forward-looking planning lives under [Blueprint](../blueprint/README.md).

## Stage Summary

- Stage 0: complete
- Stage 1: largely complete
- Stage 2: partially complete
- Stage 3: early groundwork only
- Stage 4: not started in practice
- Stage 5: interface skeleton only

## Implemented Now

### Backend platform

- FastAPI backend with explicit domain, application, adapter, and runtime layers
- durable run storage through `SqlAlchemyRunRepository`
- repo-local SQLite defaults, with Postgres support through configuration
- run persistence for config, metrics, orders, fills, positions, notes, equity curve, and provenance payloads

### Market data

- Binance-backed `MarketDataPort` adapter
- tracked-symbol sync and historical backfill
- duplicate avoidance, lag tracking, and gap reporting
- background sync job started from the app lifespan when Binance is active
- seeded market-data adapter still available for tests and fixture-driven flows

### Strategy and execution

- native runtime lane
- Freqtrade reference runtime lane for NostalgiaForInfinity backtests
- decision-engine lane contract through `DecisionEnginePort`
- runtime decomposition into `DataEngine`, `ExecutionEngine`, `RiskEngine`, `StateCache`, `RunSupervisor`, and `ExecutionModeService`
- strategy snapshots and parameter snapshots stored in run provenance

### Research workflow

- backtest execution with durable run lookup
- replay-based sandbox preview flow for native strategies
- run history listing and filtering by mode, strategy id, and strategy version
- run comparison API and control-room comparison UI
- native vs reference benchmark provenance and artifact display
- native run provenance carries dataset identity fingerprints for candle-backed inputs

### Control room

- strategy catalog grouped by runtime lane
- reference catalog panel
- market-data status with backfill and contiguous-gap summaries
- launch forms for backtests and native sandbox runs
- sandbox stop control
- side-by-side backtest comparison with narratives

## Partial or Fragile Areas

- sandbox runs are replay previews, not continuously advancing workers
- custom strategy registration exists, but registration metadata is process-local rather than durable
- run persistence is durable, but the schema is still payload-centric and not yet optimized for rich experiment querying
- native run provenance now pins dataset identity, but sync-checkpoint surfacing and full deterministic
  rerun workflows are not complete
- decision-engine support exists only as an interface and template strategy, not as a production research lane

## Not Implemented Yet

- continuous sandbox worker model with heartbeat and restart recovery
- operator alerts for stale data, sync failures, worker crashes, and risk breaches
- operator event log and audit trail
- live exchange execution adapter and kill-switch workflow
- reconciliation against live exchange state after restart or faults
- prompt versioning, raw trace persistence, and replay harness for LLM decisions

## Immediate Next Priorities

1. Harden reproducibility and dataset lineage so repeated runs can be proven equivalent.
2. Finish Stage 2 experiment workflow features such as durable strategy lifecycle, tags, presets, and richer exports.
3. Replace replay-style sandbox semantics with an actual long-running worker model.
4. Add alerts, operator events, and audit primitives before any live path work.
5. Keep the LLM lane isolated until trace storage, fallback, and replay tooling exist.
